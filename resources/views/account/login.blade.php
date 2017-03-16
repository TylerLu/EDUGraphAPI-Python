@extends('layouts.app')

@section('before.css')
@endsection

@section('content')
    <div class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li><a href="https://edugraphapidev.azurewebsites.net/">Home</a></li>
                </ul>

                <ul class="nav navbar-nav navbar-right">
                    <li><a href="https://edugraphapidev.azurewebsites.net/Account/Register" id="registerLink">Register</a></li>
                    <li><a href="https://edugraphapidev.azurewebsites.net/Account/Login" id="loginLink">Log in</a></li>
                </ul>

            </div>
        </div>
    </div>
    <div class="containerbg">
        <div class="container body-content">

            <div class="loginbody">
                <div class="row">
                    <div class="col-md-5">
                        <section id="loginForm">
                            <form action="{{ route('account.login') }}" class="form-horizontal" method="post" role="form" novalidate="novalidate">
                                {{ csrf_field() }}
                                <div class="form-group">
                                    <div class="col-md-12">
                                        <input class="form-control logincontrol" data-val="true" data-val-email="The Email field is not a valid e-mail address." data-val-required="The Email field is required." id="Email" name="email" placeholder="Email" type="text" value="">
                                        <span class="field-validation-valid text-danger" data-valmsg-for="Email" data-valmsg-replace="true"></span>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <div class="col-md-12">
                                        <input class="form-control logincontrol" data-val="true" data-val-required="The Password field is required." id="Password" name="password" placeholder="Password" type="password">
                                        <span class="field-validation-valid text-danger" data-valmsg-for="Password" data-valmsg-replace="true"></span>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <div class="margin-left-20 col-md-10">
                                        <div class="checkbox">
                                            <input data-val="true" data-val-required="The Remember me? field is required." id="RememberMe" name="RememberMe" type="checkbox" value="true"><input name="RememberMe" type="hidden" value="false">
                                            <label for="RememberMe">Remember me?</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <div class=" col-md-10">
                                        <input type="submit" value="Sign in" class="btn btn-default btn-local-login">
                                    </div>
                                </div>
                                <p>
                                    <a href="{{ route('account.register') }}">Register as a new user</a>
                                </p>
                            </form>            </section>
                    </div>
                    <div class="col-md-5">
                        <section id="socialLoginForm">


                            <h4 class="margin-btm-20">Use your school account</h4>
                            <a href="{{route('login.oauth')}}">Log in using your Microsoft Work or school account</a>

                        </section>
                    </div>
                </div>
            </div>


            <footer></footer>
        </div>
    </div>

    <div class="demo-helper-control collapsed">
        <div class="header">DEMO HELPER</div>
        <div class="header-right-shadow-mask"></div>
        <div class="body">
            <p class="desc">Code sample links for this page:</p>
            <ul>
                <li>
                    <p class="title">Controller</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Controllers/AccountController.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Controllers/AccountController.cs</a></p>
                </li>
                <li>
                    <p class="title">View</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Views/Account/Login.cshtml" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Views/Account/Login.cshtml</a></p>
                </li>
                <li>
                    <p class="title">LoginViewModel</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Models/AccountViewModels.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Models/AccountViewModels.cs</a></p>
                </li>
            </ul>
        </div>
    </div>

@endsection

