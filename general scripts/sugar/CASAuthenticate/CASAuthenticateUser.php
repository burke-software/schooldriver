<?php
if(!defined('sugarEntry') || !sugarEntry) die('Not A Valid Entry Point');

require_once('modules/Users/authentication/LDAPAuthenticate/LDAPConfigs/default.php');
require_once('modules/Users/authentication/SugarAuthenticate/SugarAuthenticateUser.php');
include_once('/usr/share/php/CAS.php');
define('DEFAULT_PORT', 389);
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
            return true; 
        }
     }//end loadUserOnlogin()
  
   /**********************************************************************************************************************
    * Attempt to authenticate the user via CAS SSO
    ***********************************************************************************************************************/    
    function authUser() {
        $cas_server = 'cas.cristoreyny.org';
        phpCAS::client(CAS_VERSION_2_0,$cas_server,443,'cas');
        phpCAS::setNoCasServerValidation();
        phpCAS::forceAuthentication();
        $authenticated = phpCAS::isAuthenticated();
        if ($authenticated)
        {   
            $user_name = phpCAS::getUser();

		    $dbresult = $GLOBALS['db']->query("SELECT id, status FROM users WHERE user_name='" . $user_name . "' AND deleted = 0");			
            //user already exists use this oe
            if($row = $GLOBALS['db']->fetchByAssoc($dbresult)){
                if($row['status'] != 'Inactive')
                    return $this->loadUserOnSession($row['id']);
                else
                    return '';
            }
       	    echo 'Not authorized user. You may need to ask an administrator to give you access to SugarCRM. You may try logging in again <a href="https://'.$cas_server.':443/cas/logout?service=http://'.$_SERVER['SERVER_NAME'].'">here</a>';
		    die();
            return ""; // SSO authentication was successful
        }
        else // not authenticated in CAS.
        {
            return;
        }
    }//end authenticateSSO();

      
/************************************************************************************************************/
/************************************************************************************************************/

}//End CASAuthenticateUSer class.

?>

