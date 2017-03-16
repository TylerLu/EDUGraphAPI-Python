<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\User;
use Input;
use Validator;
use Hash;

class IndexController extends Controller
{

    function index(){

        return 'welcome  '.\Auth::user()->email;
    }
}
