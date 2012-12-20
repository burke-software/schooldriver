# ------------------------------------------------------------------------------
import os, os.path, subprocess, md5, shutil, random
from appy.shared.utils import getOsTempFolder, FolderDeleter, cleanFolder

# ------------------------------------------------------------------------------
debianInfo = '''Package: python-appy%s
Version: %s
Architecture: all
Maintainer: Gaetan Delannay <gaetan.delannay@geezteem.com>
Installed-Size: %d
Depends: python (>= %s)%s
Section: python
Priority: optional
Homepage: http://appyframework.org
Description: Appy builds simple but complex web Python apps.
'''
appCtl = '''#! /usr/lib/zope2.12/bin/python
import sys
from appy.bin.zopectl import ZopeRunner
args = ' '.join(sys.argv[1:])
sys.argv = [sys.argv[0], '-C', '/etc/%s.conf', args]
ZopeRunner().run()
'''
appRun = '''#! /bin/sh
exec "/usr/lib/zope2.12/bin/runzope" -C "/etc/%s.conf" "$@"
'''
ooStart = '#! /bin/sh\nsoffice -invisible -headless -nofirststartwizard ' \
          '"-accept=socket,host=localhost,port=2002;urp;"'
zopeConf = '''# Zope configuration.
%%define INSTANCE %s
%%define DATA %s
%%define LOG %s
%%define HTTPPORT %s
%%define ZOPE_USER zope

instancehome $INSTANCE
effective-user $ZOPE_USER
%s
<eventlog>
  level info
  <logfile>
    path $LOG/event.log
    level info
  </logfile>
</eventlog>
<logger access>
  level WARN
  <logfile>
    path $LOG/Z2.log
    format %%(message)s
  </logfile>
</logger>
<http-server>
  address $HTTPPORT
</http-server>
<zodb_db main>
  <filestorage>
    path $DATA/Data.fs
  </filestorage>
  mount-point /
</zodb_db>
<zodb_db temporary>
  <temporarystorage>
   name temporary storage for sessioning
  </temporarystorage>
  mount-point /temp_folder
  container-class Products.TemporaryFolder.TemporaryContainer
</zodb_db>
'''
# initScript below will be used to define the scripts that will run the
# app-powered Zope instance and OpenOffice in server mode at boot time.
initScript = '''#! /bin/sh
### BEGIN INIT INFO
# Provides:          %s
# Required-Start:    $syslog $remote_fs
# Required-Stop:     $syslog $remote_fs
# Should-Start:      $remote_fs
# Should-Stop:       $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start %s
# Description:       %s
### END INIT INFO

case "$1" in
  start)
    %s
    ;;
  restart|reload|force-reload)
    %s
    ;;
  stop)
    %s
    ;;
  *)
    echo "Usage: $0 start|restart|stop" >&2
    exit 3
    ;;
esac
exit 0
'''

class Debianizer:
    '''This class allows to produce a Debian package from a Python (Appy)
       package.'''

    def __init__(self, app, out, appVersion='0.1.0',
                 pythonVersions=('2.6',), zopePort=8080,
                 depends=('zope2.12', 'openoffice.org', 'imagemagick'),
                 sign=False):
        # app is the path to the Python package to Debianize.
        self.app = app
        self.appName = os.path.basename(app)
        self.appNameLower = self.appName.lower()
        # Must we sign the Debian package? If yes, we make the assumption that
        # the currently logged user has a public/private key pair in ~/.gnupg,
        # generated with command "gpg --gen-key".
        self.sign = sign
        # out is the folder where the Debian package will be generated.
        self.out = out
        # What is the version number for this app ?
        self.appVersion = appVersion
        # On which Python versions will the Debian package depend?
        self.pythonVersions = pythonVersions
        # Port for Zope
        self.zopePort = zopePort
        # Debian package dependencies
        self.depends = depends
        # Zope 2.12 requires Python 2.6
        if 'zope2.12' in depends: self.pythonVersions = ('2.6',)

    def run(self):
        '''Generates the Debian package.'''
        curdir = os.getcwd()
        j = os.path.join
        tempFolder = getOsTempFolder()
        # Create, in the temp folder, the required sub-structure for the Debian
        # package.
        debFolder = j(tempFolder, 'debian')
        if os.path.exists(debFolder):
            FolderDeleter.delete(debFolder)
        # Copy the Python package into it
        srcFolder = j(debFolder, 'usr', 'lib')
        for version in self.pythonVersions:
            libFolder = j(srcFolder, 'python%s' % version)
            os.makedirs(libFolder)
            destFolder = j(libFolder, self.appName)
            shutil.copytree(self.app, destFolder)
            # Clean dest folder (.svn/.bzr files)
            cleanFolder(destFolder, folders=('.svn', '.bzr'))
        # When packaging Appy itself, everything is in /usr/lib/pythonX. When
        # packaging an Appy app, we will generate more files for creating a
        # running instance.
        if self.appName != 'appy':
            # Create the folders that will collectively represent the deployed
            # Zope instance.
            binFolder = j(debFolder, 'usr', 'bin')
            os.makedirs(binFolder)
            # <app>ctl
            name = '%s/%sctl' % (binFolder, self.appNameLower)
            f = file(name, 'w')
            f.write(appCtl % self.appNameLower)
            os.chmod(name, 0744) # Make it executable by owner.
            f.close()
            # <app>run
            name = '%s/%srun' % (binFolder, self.appNameLower)
            f = file(name, 'w')
            f.write(appRun % self.appNameLower)
            os.chmod(name, 0744) # Make it executable by owner.
            f.close()
            # startoo
            name = '%s/startoo' % binFolder
            f = file(name, 'w')
            f.write(ooStart)
            f.close()
            os.chmod(name, 0744) # Make it executable by owner.
            # /var/lib/<app> (will store Data.fs, lock files, etc)
            varLibFolder = j(debFolder, 'var', 'lib', self.appNameLower)
            os.makedirs(varLibFolder)
            f = file('%s/README' % varLibFolder, 'w')
            f.write('This folder stores the %s database.\n' % self.appName)
            f.close()
            # /var/log/<app> (will store event.log and Z2.log)
            varLogFolder = j(debFolder, 'var', 'log', self.appNameLower)
            os.makedirs(varLogFolder)
            f = file('%s/README' % varLogFolder, 'w')
            f.write('This folder stores the log files for %s.\n' % self.appName)
            f.close()
            # /etc/<app>.conf (Zope configuration file)
            etcFolder = j(debFolder, 'etc')
            os.makedirs(etcFolder)
            name = '%s/%s.conf' % (etcFolder, self.appNameLower)
            n = self.appNameLower
            f = file(name, 'w')
            productsFolder = '/usr/lib/python%s/%s/zope' % \
                             (self.pythonVersions[0], self.appName)
            f.write(zopeConf % ('/var/lib/%s' % n, '/var/lib/%s' % n,
                                '/var/log/%s' % n, str(self.zopePort),
                                'products %s\n' % productsFolder))
            f.close()
            # /etc/init.d/<app> (start the app at boot time)
            initdFolder = j(etcFolder, 'init.d')
            os.makedirs(initdFolder)
            name = '%s/%s' % (initdFolder, self.appNameLower)
            f = file(name, 'w')
            n = self.appNameLower
            f.write(initScript % (n, n, 'Start Zope with the Appy-based %s ' \
                                  'application.' % n, '%sctl start' % n,
                                  '%sctl restart' % n, '%sctl stop' % n))
            f.close()
            os.chmod(name, 0744) # Make it executable by owner.
            # /etc/init.d/oo (start OpenOffice at boot time)
            name = '%s/oo' % initdFolder
            f = file(name, 'w')
            f.write(initScript % ('oo', 'oo', 'Start OpenOffice in server mode',
                                  'startoo', 'startoo', "#Can't stop OO."))
            f.write('\n')
            f.close()
            os.chmod(name, 0744) # Make it executable by owner.
        # Get the size of the app, in Kb.
        os.chdir(tempFolder)
        cmd = subprocess.Popen(['du', '-b', '-s', 'debian'],
                               stdout=subprocess.PIPE)
        size = int(int(cmd.stdout.read().split()[0])/1024.0)
        os.chdir(debFolder)
        # Create data.tar.gz based on it.
        os.system('tar czvf data.tar.gz *')
        # Create the control file
        f = file('control', 'w')
        nameSuffix = ''
        dependencies = []
        if self.appName != 'appy':
            nameSuffix = '-%s' % self.appNameLower
            dependencies.append('python-appy')
        if self.depends:
            for d in self.depends: dependencies.append(d)
        depends = ''
        if dependencies:
            depends = ', ' + ', '.join(dependencies)
        f.write(debianInfo % (nameSuffix, self.appVersion, size,
                              self.pythonVersions[0], depends))
        f.close()
        # Create md5sum file
        f = file('md5sums', 'w')
        toWalk = ['usr']
        if self.appName != 'appy':
            toWalk += ['etc', 'var']
        for folderToWalk in toWalk:
            for dir, dirnames, filenames in os.walk(folderToWalk):
                for name in filenames:
                    m = md5.new()
                    pathName = j(dir, name)
                    currentFile = file(pathName, 'rb')
                    while True:
                        data = currentFile.read(8096)
                        if not data:
                            break
                        m.update(data)
                    currentFile.close()
                    # Add the md5 sum to the file
                    f.write('%s  %s\n' % (m.hexdigest(), pathName))
        f.close()
        # Create postinst, a script that will:
        # - bytecompile Python files after the Debian install
        # - change ownership of some files if required
        # - [in the case of an app-package] call update-rc.d for starting it at
        #   boot time.
        f = file('postinst', 'w')
        content = '#!/bin/sh\nset -e\n'
        for version in self.pythonVersions:
            bin = '/usr/bin/python%s' % version
            lib = '/usr/lib/python%s' % version
            cmds = ' %s -m compileall -q %s/%s 2> /dev/null\n' % (bin, lib,
                                                                  self.appName)
            content += 'if [ -e %s ]\nthen\n%sfi\n' % (bin, cmds)
        if self.appName != 'appy':
            # Allow user "zope", that runs the Zope instance, to write the
            # database and log files.
            content += 'chown -R zope:root /var/lib/%s\n' % self.appNameLower
            content += 'chown -R zope:root /var/log/%s\n' % self.appNameLower
            # Call update-rc.d for starting the app at boot time
            content += 'update-rc.d %s defaults\n' % self.appNameLower
            content += 'update-rc.d oo defaults\n'
            # (re-)start the app
            content += '%sctl restart\n' % self.appNameLower
            # (re-)start oo
            content += 'startoo\n'
        f.write(content)
        f.close()
        # Create prerm, a script that will remove all pyc files before removing
        # the Debian package.
        f = file('prerm', 'w')
        content = '#!/bin/sh\nset -e\n'
        for version in self.pythonVersions:
            content += 'find /usr/lib/python%s/%s -name "*.pyc" -delete\n' % \
                       (version, self.appName)
        f.write(content)
        f.close()
        # Create control.tar.gz
        os.system('tar czvf control.tar.gz ./control ./md5sums ./postinst ' \
                  './prerm')
        # Create debian-binary
        f = file('debian-binary', 'w')
        f.write('2.0\n')
        f.close()
        # Create the signature if required
        if self.sign:
            # Create the concatenated version of all files within the deb
            os.system('cat debian-binary control.tar.gz data.tar.gz > ' \
                      '/tmp/combined-contents')
            os.system('gpg -abs -o _gpgorigin /tmp/combined-contents')
            signFile = '_gpgorigin '
            os.remove('/tmp/combined-contents')
            # Export the public key and name it according to its ID as found by
            # analyzing the result of command "gpg --fingerprint".
            cmd = subprocess.Popen(['gpg', '--fingerprint'],
                                   stdout=subprocess.PIPE)
            fingerprint = cmd.stdout.read().split('\n')
            id = 'pubkey'
            for line in fingerprint:
                if '=' not in line: continue
                id = line.split('=')[1].strip()
                id = ''.join(id.split()[-4:])
                break
            os.system('gpg --export -a > %s/%s.asc' % (self.out, id))
        else:
            signFile = ''
        # Create the .deb package
        debName = 'python-appy%s-%s.deb' % (nameSuffix, self.appVersion)
        os.system('ar -r %s %sdebian-binary control.tar.gz data.tar.gz' % \
                  (debName, signFile))
        # Move it to self.out
        os.rename(j(debFolder, debName), j(self.out, debName))
        # Clean temp files
        FolderDeleter.delete(debFolder)
        os.chdir(curdir)

# ------------------------------------------------------------------------------
definitionJson = '''{
  "name": "%s",
  "description": "%s, a Appy-based application",
  "packages": [{"name": "python-appy" }, {"name": "python-appy-%s" }],
  "files": [
    { "group": "root", "mode": "644", "name": "%s.conf",
      "owner": "root", "path": "/etc/%s.conf",
      "template": "%s"
    }],
  "handlers": [
    { "on": ["_install"] },
    { "on": ["_uninstall" ] },
    { "on": ["%s_http_port"],
      "do": [
        { "action": "update", "resource": "file://%s.conf" }, 
        { "action": "restart", "resource": "service://%s" }
      ]}
    ],
  "services": [
    { "name": "%s", "enabled": "true", "running": "false" }, 
    { "name": "oo",  "enabled": "true",  "running": "false" }]
}
'''
definitionJsonConf = '''{
  "name": "%s.conf",
  "uuid": "%s",
  "parameters": [
    { "key": "%s_http_port",  "name": "%s HTTP port",
      "description": "%s HTTP port for the Zope process",
      "value": "8080"}
  ]
}
'''

class Cortexer:
    '''This class allows to produce a Cortex application definition for
       a Debianized Python/Appy application.

       Once the "cortex.admin" folder and its content has been generated, in
       order to push the app definition into Cortex, go in the folder where
       "cortex.admin" lies and type (command-line tool "cortex" must
       be installed):

       cortex sync push --api http://<cortex-host-ip>/api
    '''
    def __init__(self, app, pythonVersions=('2.6',)):
        self.appName = os.path.basename(app)
        self.pythonVersions = pythonVersions
        appFolder = os.path.dirname(app)
        # Prepare the output folder (remove any existing one)
        cortexFolder = os.path.join(appFolder, 'cortex.admin')
        if os.path.exists(cortexFolder):
            FolderDeleter.delete(cortexFolder)
        allFolders = os.path.join(cortexFolder, 'applications', self.appName)
        os.makedirs(allFolders)
        self.out = allFolders

    uuidChars= ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    def generateUid(self):
        '''Generates a 32-chars-wide UID for identifying the configuration file
           in the Cortex DB.'''
        res = ''
        for i in range(32):
            res += self.uuidChars[random.randint(0,15)]
        return res

    def run(self):
        # Create the root app description file "definition.json".
        uid = self.generateUid()
        name = os.path.join(self.out, 'definition.json')
        f = file(name, 'w')
        n = self.appName
        nl = self.appName.lower()
        f.write(definitionJson % (n, n, nl, nl, nl, uid, nl, nl, nl, nl))
        f.close()
        # Create the folder corresponding to the config file, and its content.
        confFolder = os.path.join(self.out, '%s.conf' % nl)
        os.mkdir(confFolder)
        # Create the definition file for this config file, that will contain
        # the names of Cortex-managed variables within the configuration file.
        name = os.path.join(confFolder, 'definition.json')
        f = file(name, 'w')
        f.write(definitionJsonConf % (nl, uid, nl, n, n))
        f.close()
        # Create the Zope config file, with Cortex-like variables within in.
        name = os.path.join(confFolder, '%s.conf' % nl)
        f = file(name, 'w')
        productsFolder='/usr/lib/python%s/%s/zope' % (self.pythonVersions[0],n)
        f.write(zopeConf % ('/var/lib/%s' % n, '/var/lib/%s' % n,
                            '/var/log/%s' % n, '${%s_http_port}' % nl,
                            'products %s\n' % productsFolder))
        f.close()
# ------------------------------------------------------------------------------
