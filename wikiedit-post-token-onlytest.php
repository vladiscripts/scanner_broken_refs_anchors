<?php

require 'wikilogin_passords.php';

$wikiapi_url = 'https://ru.wikipedia.org/w/api.php';
$cookies_file = 'cookie.txt';

function http_post_query($url, $parameters, $do_cookies = false, $cookies_file = '') {
	$curl = curl_init();
	curl_setopt($curl, CURLOPT_URL, $url);
	curl_setopt($curl, CURLOPT_HEADER, false);
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($curl, CURLOPT_POST, true);
	curl_setopt($curl, CURLOPT_POSTFIELDS, $parameters);
	//curl_setopt($curl, CURLOPT_COOKIE, true);
	if ($do_cookies == 'save')
		curl_setopt($curl, CURLOPT_COOKIEJAR, $cookies_file);
	elseif ($do_cookies == 'send')
		curl_setopt($curl, CURLOPT_COOKIEFILE, $cookies_file);
	elseif ($do_cookies == 'both')
		curl_setopt($curl, CURLOPT_COOKIEJAR, $cookies_file);
		curl_setopt($curl, CURLOPT_COOKIEFILE, $cookies_file);
	$result = curl_exec($curl);
	//preg_match('/^Set-Cookie: (.*?);/m', $out, $m);
	//var_dump(parse_url($m[1]));
	curl_close($curl);
	return $result;
}

function wikiapi_logintoken() {
	global $wikiapi_url, $cookies_file;
	$parameters = array('action' => 'query', 'meta' => 'tokens', 'type' => 'login', 'format' => 'json');
	$result = http_post_query($wikiapi_url, $parameters, $do_cookies = 'save', $cookies_file);
	echo $result . EOL;
	$r_obj = json_decode($result);	
	return $r_obj->query->tokens->logintoken;
}

function wikiapi_login($token) {
    //$bot = 'ruwiki_mark_broken_ref_anchors';

	global $wikiapi_url, $cookies_file;
	$parameters = array('action' => 'login', 'lgname' => $full_bot_login, 'lgpassword' => $bot_pw, 'format' => 'json', 'lgtoken' => $token);
	$result = http_post_query($wikiapi_url, $parameters, $do_cookies = 'both', $cookies_file);
	print $result . EOL;
	$r_obj = json_decode($result);	
	return $r_obj->login->lgtoken;
}


function wikiapi_csrf_token() {
	global $wikiapi_url, $cookies_file;
	$parameters = array('action' => 'query', 'meta' => 'tokens', 'format' => 'json');
	$result = http_post_query($wikiapi_url, $parameters, $do_cookies = 'save', $cookies_file);
	print $result . EOL;
	$r_obj = json_decode($result);
	return $r_obj->query->tokens->csrftoken;
}


function wikiapi_edit($title, $appendtext, $summary, $token)
{
	$parameters = array('action' => 'edit', 'title' => $title, 'appendtext' => $appendtext, 'summary' => $summary, 'format' => 'json', 'token' => $token);
	global $wikiapi_url, $cookies_file;
	$result = http_post_query($wikiapi_url, $parameters, $do_cookies = 'send', $cookies_file);
	echo $result .EOL;
	$r_obj = json_decode($result);
	$token = $r_obj->login->token;
	$cookieprefix = $r_obj->login->cookieprefix;
	$sessionid = $r_obj->login->sessionid;
}

$need_login = 0;
if ($need_login) {
	$logintoken = wikiapi_logintoken();
	$lgtoken = wikiapi_login($logintoken);
}

$need_edit_login = 0;
$csrftoken = "7eed99e2637dea3a27d6a9855521dbb057a8e67e+\\";
if ($need_edit_login) {
	$csrftoken = wikiapi_csrf_token();
}

$title = 'Википедия:Песочница';
$appendtext = '{{tpl}}';
$summary = 'summary';
wikiapi_edit($title, $appendtext, $summary, $csrftoken);



?>