<?php
define( 'WP_CACHE', true );


/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the website, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'orionter_wp377' );

/** Database username */
define( 'DB_USER', 'orionter_wp377' );

/** Database password */
define( 'DB_PASSWORD', '7SE9-3Tp3(' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'kw6a1iggoubs7z7vgh9arxnc7ue8dmmdxq2nkzvozyxlqxlpqo68vkjxmpgivrhs' );
define( 'SECURE_AUTH_KEY',  '5qausio9rfx4bzt9ryqvpxsvhkn8vtbuxgla3sciawylufz1rifi2tzgudjcrrm1' );
define( 'LOGGED_IN_KEY',    'iycj9vqj1mbzy5ibbzdiydkvthbrcpkdr1zpwvo1lxoocbpgnfwinwhtwica9ski' );
define( 'NONCE_KEY',        'zxivxb2qlnforqxipig4pwqk7senyuwfslnqe09gwnfhjhumofpnfdsf32gpp7du' );
define( 'AUTH_SALT',        'udjz6ulnhmntcypbhoqkglsfhejtkizkenrtkei8p9wqctqo9wrbd1d0ge8agsyp' );
define( 'SECURE_AUTH_SALT', 'eunocrj9qfu8cghwqskzig6i9mu41zitefgskp3mfq23mnbkbea94eqtgtcnc34x' );
define( 'LOGGED_IN_SALT',   'dwhufsm6ckfz25ucrdkzcatsf54yim8xtenlushsmrkdo3yjk4fekum4nwafcsvy' );
define( 'NONCE_SALT',       'fvfl9b5fshrymfcxvnhekyfjsrvbhq8u25ghiyuorrxfte8ci5u5ift0azvocujo' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 *
 * At the installation time, database tables are created with the specified prefix.
 * Changing this value after WordPress is installed will make your site think
 * it has not been installed.
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/#table-prefix
 */
$table_prefix = 'wpw2_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
