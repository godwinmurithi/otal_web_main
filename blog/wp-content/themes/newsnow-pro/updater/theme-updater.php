<?php
/**
 * Easy Digital Downloads Theme Updater
 *
 * @package EDD Sample Theme
 */

// Includes the files needed for the theme updater
if ( !class_exists( 'EDD_Theme_Updater_Admin' ) ) {
	include( dirname( __FILE__ ) . '/theme-updater-admin.php' );
}

// Loads the updater classes
$updater = new EDD_Theme_Updater_Admin(

	// Config settings
	$config = array(
		'remote_api_url' => 'https://www.freshthemes.com', // Site where EDD is hosted
		'item_name'      => 'NewsNow Pro WordPress Theme', // Name of theme
		'theme_slug'     => 'newsnow-pro', // Theme slug
		'version'        => '2.0.1', // The current version of this theme
		'author'         => 'FreshThemes', // The author of this theme
		'download_id'    => '', // Optional, used for generating a license renewal link
		'renew_url'      => '', // Optional, allows for a custom license renewal link
		'beta'           => false, // Optional, set to true to opt into beta versions
	),

	// Strings
	$strings = array(
		'theme-license'             => __( 'Theme License', 'newsnow-pro' ),
		'enter-key'                 => __( 'Enter your theme license key.', 'newsnow-pro' ),
		'license-key'               => __( 'License Key', 'newsnow-pro' ),
		'license-action'            => __( 'License Action', 'newsnow-pro' ),
		'deactivate-license'        => __( 'Deactivate License', 'newsnow-pro' ),
		'activate-license'          => __( 'Activate License', 'newsnow-pro' ),
		'status-unknown'            => __( 'License status is unknown.', 'newsnow-pro' ),
		'renew'                     => __( 'Renew?', 'newsnow-pro' ),
		'unlimited'                 => __( 'unlimited', 'newsnow-pro' ),
		'license-key-is-active'     => __( 'License key is active.', 'newsnow-pro' ),
		'expires%s'                 => __( 'Expires %s.', 'newsnow-pro' ),
		'expires-never'             => __( 'Lifetime License.', 'newsnow-pro' ),
		'%1$s/%2$-sites'            => __( 'You have %1$s / %2$s sites activated.', 'newsnow-pro' ),
		'license-key-expired-%s'    => __( 'License key expired %s.', 'newsnow-pro' ),
		'license-key-expired'       => __( 'License key has expired.', 'newsnow-pro' ),
		'license-keys-do-not-match' => __( 'License keys do not match.', 'newsnow-pro' ),
		'license-is-inactive'       => __( 'License is inactive.', 'newsnow-pro' ),
		'license-key-is-disabled'   => __( 'License key is disabled.', 'newsnow-pro' ),
		'site-is-inactive'          => __( 'Site is inactive.', 'newsnow-pro' ),
		'license-status-unknown'    => __( 'License status is unknown.', 'newsnow-pro' ),
		'update-notice'             => __( "Updating this theme will lose any customizations you have made. 'Cancel' to stop, 'OK' to update.", 'newsnow-pro' ),
		'update-available'          => __('<strong>%1$s %2$s</strong> is available. <a href="%3$s" class="thickbox" title="%4s">Check out what\'s new</a> or <a href="%5$s"%6$s>update now</a>.', 'newsnow-pro' ),
	)

);
