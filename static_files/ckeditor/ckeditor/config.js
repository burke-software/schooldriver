/**
 * @license Copyright (c) 2003-2013, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.html or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For the complete reference:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbar = [
          ['Bold', 'Italic', 'Underline', 'Subscript','Superscript',
              '-', 'Image', 'Link', 'Unlink', 'SpecialChar', 'equation',
              '-', 'Format',
              '-', 'Maximize',
              '-', 'Table',
              '-', 'BulletedList', 'NumberedList',
              '-', 'PasteText','PasteFromWord',]
	];
        
        config.extraPlugins = 'equation';
        config.removePlugins = 'scayt,menubutton,contextmenu,liststyle,tabletools,tableresize,elementspath';
        config.disableNativeSpellChecker = false;
        config.filebrowserWindowWidth = 940;
        config.filebrowserWindowHeight = 725;
        config.filebrowserUploadUrl = '/ckeditor/upload/';
        config.filebrowserBrowseUrl = '/ckeditor/browse/';
	// Se the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';

	// Make dialogs simpler.
	config.removeDialogTabs = 'image:advanced;link:advanced';
};
