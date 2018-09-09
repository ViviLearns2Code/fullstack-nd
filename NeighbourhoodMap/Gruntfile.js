module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      build: {
        expand: true,
        cwd: "dist/",
        src: "**/*.js",
        dest: "dist/"
      }
    },
    concat: {
      dist: {
        src: ['node_modules/babel-polyfill/dist/polyfill.min.js','dist/js/main.js'],
        dest: 'dist/js/main.js'
      }
    },
    cssmin: {
      build: {
        expand: true,
        cwd: "src/",
        src: "**/*.css",
        dest: "dist/"
      }
    },
    htmlmin: {
      build: {
        src: "src/index.html",
        dest: "dist/index.html"
      }
    }
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-htmlmin');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-concat');

  // Default task(s).
  grunt.registerTask('default', ['uglify','concat','htmlmin','cssmin']);

};