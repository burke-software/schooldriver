/**
 * Installation:
 * 1. Install Grunt CLI (`npm install -g grunt-cli`)
 * 1. Install Grunt 0.4.0 and other dependencies (`npm install`)
 *
 * Build:
 * Execute `grunt` from root directory of this directory (where Gruntfile.js is)
 * To execute automatically after each change, execute `grunt --force default watch`
 * To execute build followed by the test run, execute `grunt test`
 *
 * See http://gruntjs.com/getting-started for more information about Grunt
 */
module.exports = function (grunt) {
    grunt.initConfig({

            pkg: grunt.file.readJSON('package.json'),


            html2js: {
                commonDirectives: {
                    options: {
                        module: 'gradeBookApp.templates',      // ANGULAR MODULE NAME
                        base: 'static_files/app/app-source/modules/',          // REMOVE PATH FROM FILE
                        htmlmin: {
                            collapseWhitespace: true,
                            removeComments: true
                        }
                    },
                    dest: 'tmp/commonDirectives.js',
                    src: [
                        'static_files/app/app-source/modules/**/**/*.html',
                        'static_files/app/app-source/modules/**/**/**/*.html'
                    ]
                }
            },



            app: {
                all: [
                    'static_files/app/app-source/directives/**/*.js',
                    'static_files/app/app-source/modules/**/*.js',
                    'static_files/app/app-source/services/*.js'
                ]
            },

            concat: {
                dist: {
                    files: {
                        'static_files/app/gradebook.js': [
                            'static_files/app/app-source/gradebook.js',
                            '<%= app.all %>',
                            'tmp/commonDirectives.js'

                        ]
                    }
                }
            },

            uglify: {
                my_target: {
                    files: {
                        'static_files/app/gradebook.min.js': ['static_files/app/gradebook.js']
                    }
                }
            },

            watch: {
                options: {
                    livereload: true //works with Chrome LiveReload extension. See: https://github.com/gruntjs/grunt-contrib-watch
                },
                files: [
                    'static_files/app/app-source/modules/**/**/*.html',
                    'static_files/app/app-source/modules/**/**/*.js',
                    'static_files/app/app-source/*.js',
                    'static_files/app/app-source/**/*.js',
                    'static_files/app/app-source/**/**/*.js',
                    'static_files/app/app-source/**/**/**/*.js',
                    'static_files/app/app-source/**/**/*.html'
                ],
                tasks: ['default']
            },

            clean: {
                dist: ['tmp']
            }

        }
    );

    // DEFAULT TASKS
    grunt.registerTask('default', [
        "html2js",
        "concat",
        "uglify",
        "clean"
    ]);

    grunt.loadNpmTasks('grunt-html2js');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-watch');
};
