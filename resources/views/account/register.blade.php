@extends('layouts.app')

@section('before.css')
@endsection

@section('content')
    <h2>Register.</h2>
    <h42>Create a new account.</h4>
        <form action="{{ route('account.register')}}" class="form-horizontal" method="post" role="form" novalidate="novalidate">
            {{ csrf_field()}}
            <hr>
            <div class="validation-summary-valid text-danger" data-valmsg-summary="true"><ul><li style="display:none"></li>
                </ul></div>    <div class="form-group">
                <label class="col-md-2 control-label" for="Email">Email</label>
                <div class="col-md-10">
                    <input class="form-control" data-val="true" data-val-email="The Email field is not a valid e-mail address." data-val-required="The Email field is required." id="Email" name="email" type="text" value="">
                </div>
            </div>
            <div class="form-group">
                <label class="col-md-2 control-label" for="Password">Password</label>
                <div class="col-md-10">
                    <input class="form-control" data-val="true" data-val-length="The Password must be at least 6 characters long." data-val-length-max="100" data-val-length-min="6" data-val-required="The Password field is required." id="Password" name="password" type="password">
                </div>
            </div>
            <div class="form-group">
                <label class="col-md-2 control-label" for="ConfirmPassword">Confirm password</label>
                <div class="col-md-10">
                    <input class="form-control" data-val="true" data-val-equalto="The password and confirmation password do not match." data-val-equalto-other="*.Password" id="ConfirmPassword" name="password_confirmation" type="password">
                </div>
            </div>    <div class="form-group">
                <label class="col-md-2 control-label" for="FavoriteColor">Favorite color</label>
                <div class="col-md-10">
                    <select name="favorite_color" id="FavoriteColor" class="form-control">
                        <option value="#2F19FF">Blue</option>
                        <option value="#127605">Green</option>
                        <option value="#535353">Grey</option>
                    </select>

                </div>
            </div>
            <div class="form-group">
                <div class="col-md-offset-2 col-md-10">
                    <input type="submit" class="btn btn-default" value="Register">
                </div>
            </div>
        </form>
@endsection



