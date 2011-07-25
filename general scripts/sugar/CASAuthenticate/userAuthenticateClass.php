<?php
if(!defined('sugarEntry') || !sugarEntry) die('Not A Valid Entry Point');

require_once('modules/Users/authentication/SugarAuthenticate/SugarAuthenticateUser.php');
require_once('/var/www/sugarcrm/CAS.php');


class CASAuthenticateUser extends SugarAuthenticateUser {

    /********************************************************************************
     * This is called when a user logs in 
     *
     * @param STRING $name
     * @param STRING $password
     * @return boolean
     ********************************************************************************/
     
     function loadUserOnLogin() {
     
      $name=$this->authUser();
        if(empty($name)){
           return false;              
        }
     else{
            $GLOBALS['log']->debug("Starting user load for ". $name);
            $user_id=$this->createSugarUser($name);
            $this->loadUserOnSession($user_id);

        return true; 
        }
      }//end loadUserOnlogin()
  
   /**********************************************************************************************************************
    * Attempt to authenticate the user via CAS SSO
    ***********************************************************************************************************************/
    
      function authUser() {
         phpCAS::client(CAS_VERSION_2_0,'cas.cristoreyny.org',8443,'cas');
         phpCAS::setNoCasServerValidation();
         phpCAS::forceAuthentication();
         $authenticated = phpCAS::isAuthenticated();
        if ($authenticated)
        {   
            $user_name = phpCAS::getUser();
            $query = "SELECT * from users where user_name='$user_name' and deleted=0";
            $result =$GLOBALS['db']->limitQuery($query,0,1,false);
            $row = $GLOBALS['db']->fetchByAssoc($result);
            if (!empty ($row))
            {
                $_SESSION['authenticated_user_id'] = $row['id'];
                $_SESSION['login_user_name'] = $user_name;
                $_REQUEST['user_password'] = 'foobar';
            }
            else // row in Sugar DB was empty, even though user is in CAS.
            {
              return;
            }            
           
            $action = 'Authenticate';
            $module = 'Users';
            $_REQUEST['action'] = 'Authenticate';
            $_REQUEST['module'] = 'Users';
            $_REQUEST['return_module'] = 'Users';
            $_REQUEST['action_module'] = 'Login';
                        
            return $user_name; // SSO authentication was successful
            
        }
        else // not authenticated in CAS.
        {            
          return;
        }
           
      }//end authenticateSSO();
        
   
     function createSugarUser($name) {
            $user = new User();
            $user->user_name = $name;
            $user->employee_status = 'Active';
            $user->status = 'Active';
            $user->is_admin = 0;
  <?php

if(!defined('sugarEntry') || !sugarEntry) die('Not A Valid Entry Point');

require_once('modules/Users/authentication/SugarAuthenticate/SugarAuthenticateUser.php');
require_once('/var/www/sugarcrm/CAS.php');


class CASAuthenticateUser extends SugarAuthenticateUser {

    /********************************************************************************
     * This is called when a user logs in 
     *
     * @param STRING $name
     * @param STRING $password
     * @return boolean
     ********************************************************************************/
     
     function loadUserOnLogin() {
     
      $name=$this->authUser();
        if(empty($name)){
           return false;              
        }
     else{
            $GLOBALS['log']->debug("Starting user load for ". $name);
            $user_id=$this->createSugarUser($name);
            $this->loadUserOnSession($user_id);

        return true; 
        }
      }//end loadUserOnlogin()
  
   /**********************************************************************************************************************
    * Attempt to authenticate the user via CAS SSO
    ***********************************************************************************************************************/
    
      function authUser() {
       
         phpCAS::client(CAS_VERSION_2_0,'xx.xx.xx.xx',443,'cas');
         phpCAS::setNoCasServerValidation();
         phpCAS::forceAuthentication();
         $authenticated = phpCAS::isAuthenticated();
        if ($authenticated)
        {   
  <?php

if(!defined('sugarEntry') || !sugarEntry) die('Not A Valid Entry Point');

require_once('modules/Users/authentication/SugarAuthenticate/SugarAuthenticateUser.php');
require_once('/var/www/sugarcrm/CAS.php');


class CASAuthenticateUser extends SugarAuthenticateUser {

    /********************************************************************************
     * This is called when a user logs in 
     *
     * @param STRING $name
     * @param STRING $password
     * @return boolean
     ********************************************************************************/
     
     function loadUserOnLogin() {
     
      $name=$this->authUser();
        if(empty($name)){
           return false;              
        }
     else{
            $GLOBALS['log']->debug("Starting user load for ". $name);
            $user_id=$this->createSugarUser($name);
            $this->loadUserOnSession($user_id);

        return true; 
        }
      }//end loadUserOnlogin()
  
   /**********************************************************************************************************************
    * Attempt to authenticate the user via CAS SSO
    ***********************************************************************************************************************/
    
      function authUser() {
       
         phpCAS::client(CAS_VERSION_2_0,'xx.xx.xx.xx',443,'cas');
         phpCAS::setNoCasServerValidation();
         phpCAS::forceAuthentication();
         $authenticated = phpCAS::isAuthenticated();
        if ($authenticated)
        {   
            $user_name = phpCAS::getUser();
            $query = "SELECT * from users where user_name='$user_name' and deleted=0";
            $result =$GLOBALS['db']->limitQuery($query,0,1,false);
            $row = $GLOBALS['db']->fetchByAssoc($result);
            if (!empty ($row))
            {
                $_SESSION['authenticated_user_id'] = $row['id'];
                $_SESSION['login_user_name'] = $user_name;
                $_REQUEST['user_password'] = 'foobar';
            }
            else // row in Sugar DB was empty, even though user is in CAS.
            {
              return;
            }            
           
            $action = 'Authenticate';
            $module = 'Users';
            $_REQUEST['action'] = 'Authenticate';
            $_REQUEST['module'] = 'Users';
            $_REQUEST['return_module'] = 'Users';
            $_REQUEST['action_module'] = 'Login';
                        
            return $user_name; // SSO authentication was successful
            
        }
        else // not authenticated in CAS.
        {            
          return;
        }
           
      }//end authenticateSSO();
        
   
     function createSugarUser($name) {
            $user = new User();
            $user->user_name = $name;
            $user->employee_status = 'Active';
            $user->status = 'Active';
            $user->is_admin = 0;
            
            if ($name =='admin'){
            $user->is_admin = 1;
            }
           
            $user->save();

            // Force the user to go to the home screen
            $_REQUEST['action'] = 'index';
            $_REQUEST['module'] = 'Home';

           // Return the user's GUID
           return $user->id;
    }//createSugarUser

      
/************************************************************************************************************/
/************************************************************************************************************/

}//End CASAuthenticateUSer class.

?>          $user_name = phpCAS::getUser();
            $query = "SELECT * from users where user_name='$user_name' and deleted=0";
            $result =$GLOBALS['db']->limitQuery($query,0,1,false);
            $row = $GLOBALS['db']->fetchByAssoc($result);
            if (!empty ($row))
            {
                $_SESSION['authenticated_user_id'] = $row['id'];
                $_SESSION['login_user_name'] = $user_name;
                $_REQUEST['user_password'] = 'foobar';
            }
            else // row in Sugar DB was empty, even though user is in CAS.
            {
              return;
            }            
           
            $action = 'Authenticate';
            $module = 'Users';
            $_REQUEST['action'] = 'Authenticate';
            $_REQUEST['module'] = 'Users';
            $_REQUEST['return_module'] = 'Users';
            $_REQUEST['action_module'] = 'Login';
                        
            return $user_name; // SSO authentication was successful
            
        }
        else // not authenticated in CAS.
        {            
          return;
        }
           
      }//end authenticateSSO();
        
   
     function createSugarUser($name) {
            $user = new User();
            $user->user_name = $name;
            $user->employee_status = 'Active';
            $user->status = 'Active';
            $user->is_admin = 0;
            
            if ($name =='admin'){
            $user->is_admin = 1;
            }
           
            $user->save();

            // Force the user to go to the home screen
            $_REQUEST['action'] = 'index';
            $_REQUEST['module'] = 'Home';

           // Return the user's GUID
           return $user->id;
    }//createSugarUser

      
/************************************************************************************************************/
/************************************************************************************************************/

}//End CASAuthenticateUSer class.

?>          
            if ($name =='admin'){
            $user->is_admin = 1;
            }
           
            $user->save();

            // Force the user to go to the home screen
            $_REQUEST['action'] = 'index';
            $_REQUEST['module'] = 'Home';

           // Return the user's GUID
           return $user->id;
    }//createSugarUser

      
/************************************************************************************************************/
/************************************************************************************************************/

}//End CASAuthenticateUSer class.

?>
