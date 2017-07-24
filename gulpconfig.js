var path = require('path');
var webpack = require('webpack');

var src_root = __dirname + '/webassets';
var pkg_root = path.normalize(__dirname + '/journimap/web');
var dist_root = pkg_root + '/static';

var paths = {
  src_root: src_root,
  pkg_root: pkg_root,
  dist_root: dist_root,
  src: {
    scripts: src_root + '/scripts',
    styles: src_root + '/styles',
    fonts: src_root + '/fonts',
    media: src_root + '/media',
  },
  dist: {
    js: dist_root + '/js',
    css: dist_root + '/css',
    fonts: dist_root + '/fonts',
    media: dist_root + '/media',
  },
  vendor: src_root + '/vendor',
  templates: pkg_root + '/**/*.jinja2',
};

var config = {
  optimize: false,
  paths: paths,
  manifest: {
    src: dist_root + '/**/*',
    jsonOutputName: 'manifest.json',
    jsOutputName: 'js/manifest.js',
    dest: dist_root,
  },
  fonts: {
    src: [
      './node_modules/bootstrap/dist/fonts/*',
      './node_modules/font-awesome/fonts/*',
      paths.src.fonts + '/**/*.{eot,svg,ttf,woff,woff2,otf}',
    ],
    dest: paths.dist.fonts,
  },
  media: {
    src: [
      paths.src.media + '/**/*',
    ],
    dest: paths.dist.media,
  },
  webpack: {
    entries: {
      'common': paths.src.scripts + '/common.js',
      'main': paths.src.scripts + '/main.js',
      'validator': paths.src.scripts + '/validator.js',
      'datetime-picker': paths.src.scripts + '/datetime-picker.js',
      'chart': paths.src.scripts + '/chart.js'
    },
    aliases: {

    },
    plugins: [
      new webpack.optimize.CommonsChunkPlugin({
          name: "common",
          filename: "common.js"
      }),
      new webpack.ProvidePlugin({
          $: "jquery",
          jQuery: 'jquery'
      }),
    ],
  },
  livereload: {
    // if you change the port make sure to update it in the ini as well
    host: '0.0.0.0',
    port: 35780,
  },
  sass: {
    bundles: {
      'common': {
        src: paths.src.styles + '/common.scss',
      },
      'main': {
        src: paths.src.styles + '/main.scss',
      },
    },
    dest: paths.dist.css,
  },
};

module.exports = config;
