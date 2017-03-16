<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| This file is where you may define all of the routes that are handled
| by your application. Just tell Laravel the URIs it should respond
| to using a Closure or controller method. Build something great!
|
*/


Route::any('/account/login', ['as' => 'account.login', 'uses' => 'AccountController@login']);
Route::any('/account/register', ['as' => 'account.register', 'uses' => 'AccountController@register']);

Route::any('/account/oauth', ['as' => 'login.oauth', 'uses' => 'AccountController@oauth']);

Route::any('/', ['as' => 'index', 'uses' => 'IndexController@index']);

Route::group(['middleware' => []], function () {
    Route::get('/email', ['as' => 'email.userinfo', 'uses' => 'EmailController@showUserInfo']);
    Route::post('/email', 'EmailController@sendEmail');
    Route::any('/account/link', ['as' => 'account.link', 'uses' => 'AccountController@link']);
    Route::get('/account/processlink', ['as' => 'account.processlink', 'uses' => 'AccountController@processLink']);
});

