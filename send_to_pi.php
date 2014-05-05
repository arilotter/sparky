<?php
	function get_domain($url)
{
  $pieces = parse_url($url);
  $domain = isset($pieces['host']) ? $pieces['host'] : '';
  if (preg_match('/(?P<domain>[a-z0-9][a-z0-9\-]{1,63}\.[a-z\.]{2,6})$/i', $domain, $regs)) {
    return $regs['domain'];
  }
  return false;
}

$url = $_GET['url'];
$site = explode(".", get_domain($url))[0];
if(site == "youtube") {
	popen('/var/www/youtube.sh "' . $url . '" &', 'r');
	echo "Youtube video should start in a few seconds, have a nice day!";
} else { //prolly a movie lmao
	popen('/var/www/movie.sh "' . $url . '" &', 'r');
	echo "Movie should start in a few seconds, have a nice day!";
}
?>
