<?php
// A script that runs quexf's import directory. Quexf's watch feature doesn't
// seem to work so use this. Run on cron every minute. Pid file will prevent
// it from running twice. If it does crash delete the pid from /tmp

// Import these quexf functions, notice the path
include("../functions/functions.import.php");
include("../functions/functions.xhtml.php");
include("../functions/functions.process.php");

// http://www.electrictoolbox.com/check-php-script-already-running/
class pid {

    protected $filename;
    public $already_running = false;
   
    function __construct($directory) {
       
        $this->filename = $directory . '/' . basename($_SERVER['PHP_SELF']) . '.pid';
       
        if(is_writable($this->filename) || is_writable($directory)) {
           
            if(file_exists($this->filename)) {
                $pid = (int)trim(file_get_contents($this->filename));
                if(posix_kill($pid, 0)) {
                    $this->already_running = true;
                }
            }
           
        }
        else {
            die("Cannot write to pid file '$this->filename'. Program execution halted.\n");
        }
       
        if(!$this->already_running) {
            $pid = getmypid();
            file_put_contents($this->filename, $pid);
        }
       
    }

    public function __destruct() {

        if(!$this->already_running && file_exists($this->filename) && is_writeable($this->filename)) {
            unlink($this->filename);
        }
   
    }
   
}

$pid = new pid('/tmp');
if($pid->already_running) {
    echo "Already running.\n";
    exit;
}
else {
    $dir = '/var/www/doc/filled';

    import_directory($dir);
    sleep(8); // Because cron can't do less than 1 minute, run a few times
    $dir = '/var/www/doc/filled';

    import_directory($dir);
    sleep(8);
    $dir = '/var/www/doc/filled';

    import_directory($dir);
    sleep(8);
    $dir = '/var/www/doc/filled';

    import_directory($dir);
    sleep(8);
    $dir = '/var/www/doc/filled';

    import_directory($dir);
    sleep(8);
}
?>
