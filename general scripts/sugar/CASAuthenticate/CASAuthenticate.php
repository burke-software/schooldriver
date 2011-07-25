<?php
if(!defined('sugarEntry') || !sugarEntry) die('Not A Valid Entry Point');
require_once('modules/Users/authentication/SugarAuthenticate/SugarAuthenticate.php');
require_once('/usr/share/php/CAS.php');

/********************************************************************
 * Module that allows Sugar to perform user authentication using
 *  CAS.
 *********************************************************************/

class CASAuthenticate extends SugarAuthenticate {
    var $userAuthenticateClass = 'CASAuthenticateUser';
    var $authenticationDir = 'CASAuthenticate';
      
      function CASAuthenticate(){
      parent::SugarAuthenticate();
                  require_once('modules/Users/authentication/'. $this->authenticationDir . '/'. $this->userAuthenticateClass . '.php');
        $this->userAuthenticate = new $this->userAuthenticateClass();
            $this->doCASAuth();           
          } 

      
        function doCASAuth(){
         @session_start();
                                 
        // Don't try to login if the user is logging out
        if (isset($_REQUEST['action']) && $_REQUEST['action'] == 'Logout') {
            $this->logout();
        }
        // If the user is already authenticated, do this.
        elseif (isset($_SESSION['authenticated_user_id']) ) {
            $this->sessionAuthenticate();   
            return;
        }
                   // Try to log the user in via SSO
        else {
            if ($this->userAuthenticate->loadUserOnLogin() == true) {
              parent::postLoginAuthenticate();
              header( 'Location: http://10.5.142.205' );
                 }
          else {
           
            die(); //I should redirect here.  I'm not sure on the syntax -- sorry.
                       } //end nested else.
        } // end top else.
        } //end doCASAuth()
 
     
        function sessionAuthenticate(){
        global $module, $action, $allowed_actions;
        $authenticated = false;
        $allowed_actions = array ("Authenticate", "Login"); // these are actions where the user/server keys aren't compared
        if (isset ($_SESSION['authenticated_user_id'])) {
            $GLOBALS['log']->debug("We have an authenticated user id: ".$_SESSION["authenticated_user_id"]);
            $authenticated = $this->postSessionAuthenticate();
        } else
            if (isset ($action) && isset ($module) && $action == "Authenticate" && $module == "Users") {
            $GLOBALS['log']->debug("We are NOT authenticating user now.  CAS will redirect.");
        } 
        return $authenticated;
        } //end sessionAuthenticate()

       
      function postSessionAuthenticate(){
        global $action, $allowed_actions, $sugar_config;
        $_SESSION['userTime']['last'] = time();
        $user_unique_key = (isset ($_SESSION['unique_key'])) ? $_SESSION['unique_key'] : '';
        $server_unique_key = (isset ($sugar_config['unique_key'])) ? $sugar_config['unique_key'] : '';
        
        //CHECK IF USER IS CROSSING SITES
        if (($user_unique_key != $server_unique_key) && (!in_array($action, $allowed_actions)) && (!isset ($_SESSION['login_error']))) {
            
            session_destroy();
            $post_login_nav = '';
            if (!empty ($record) && !empty ($action) && !empty ($module)) {
                $post_login_nav = "&login_module=".$module."&login_action=".$action."&login_record=".$record;
            }
            $GLOBALS['log']->debug('Destroying Session User has crossed Sites');
            //header("Location: index.php?action=Login&module=Users".$post_login_nav);
            sugar_cleanup(true);
                        die(); 
        }
        if (!$this->userAuthenticate->loadUserOnSession($_SESSION['authenticated_user_id'])) {
            session_destroy();
            //header("Location: index.php?action=Login&module=Users");
            $GLOBALS['log']->debug('Current user session does not exist redirecting to login');
            sugar_cleanup(true);
                        die(); 
               }
        $GLOBALS['log']->debug('Current user is: '.$GLOBALS['current_user']->user_name);
        return true;
          }//end postSessionAuthenticate()
  


            function logout() {
        phpCAS::setDebug();
        phpCAS::client(CAS_VERSION_2_0,'cas.cristoreyny.org',8443,'cas');
        phpCAS::setNoCasServerValidation();
        phpCAS::logout(); 
      }

}//end CASAuthenticate class 
