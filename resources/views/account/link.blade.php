@extends('layouts.app')

@section('before.css')
@endsection

@section('content')
    <body>
    <div class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/">Edu Demo App</a>
            </div>
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li><a href="/">Home</a></li>
                    <li><a href="/Admin">Admin</a></li>
                </ul>

                <form action="/Account/LogOff" class="navbar-right" id="logoutForm" method="post"><input name="__RequestVerificationToken" type="hidden" value="sWYenyrF57xI16yjPgZXb9SyvftNE_3t4rb8tFtF-6VD42l-Fvkiq2Gd5n_OQFVfpto9-ctLdXFnHlOKhy6GMt2j3oMhMTIN1OnQP9QBlrWGOIxs_sOGyLRas1bwFZ7poczCNgAeeXinTQEh8gIDig2">        <div class="userinfo">
                        <a href="javascript:void(0);" id="userinfolink">Logged in as: Admin. Hello Admin Dev <img src="/Photo/UserPhoto/03311f11-cb5b-41e2-82dc-30e0e1ec995a"></a>
                        <span class="caret" id="caret"></span>
                    </div>
                    <div class="popupcontainer" id="userinfoContainer" style="display: none;">
                        <div class="popuserinfo">
                            <div class="subitem">
                                <a href="/Manage/AboutMe">About Me</a>
                            </div>
                            <div class="subitem">
                                <a href="/link">Link</a>
                            </div>
                            <div class="subitem">
                                <a href="javascript:document.getElementById('logoutForm').submit()">Log off</a>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <div class="containerbg">
        <div class="container body-content">



            <h2>Link Office 365 &amp; Local Account</h2>
            <p>This page will enable you to link your Office 365 &amp; Local Account together to successfully use the demo application.</p>
            <hr>
            <div class="form-horizontal">
                <p>There is a local account: admin.dev@canvizEDU.onmicrosoft.com matching your O365 account.</p>
                <p>
                    <a class="btn btn-primary" disabled="disabled" href="javascript:void(0)">Continue with new Local Account</a>                    &nbsp; &nbsp;

                    <a class="btn btn-primary" href="/Link/LoginLocal">Link with existing Local Account</a> &nbsp; &nbsp;
                </p>
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
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Controllers/LinkController.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Controllers/LinkController.cs</a></p>
                </li>
                <li>
                    <p class="title">View</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Views/Link/Index.cshtml" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Views/Link/Index.cshtml</a></p>
                </li>
                <li>
                    <p class="title">ApplicationService</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Services/ApplicationService.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Services/ApplicationService.cs</a></p>
                </li>
                <li>
                    <p class="title">UserContext</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Models/UserContext.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Models/UserContext.cs</a></p>
                </li>
                <li>
                    <p class="title">AADGraphClient</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Services/GraphClients/AADGraphClient.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Services/GraphClients/AADGraphClient.cs</a></p>
                </li>
                <li>
                    <p class="title">MSGraphClient</p>
                    <p><a href="https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Services/GraphClients/MSGraphClient.cs" target="_blank">https://github.com/TylerLu/EDUGraphAPI/blob/master/src/EDUGraphAPI.Web/Services/GraphClients/MSGraphClient.cs</a></p>
                </li>
            </ul>
        </div>
    </div>


    <script type="text/javascript">
        $(function () {
            $('#skipLinkAccount').on('click', function () {
                $('#linkAccountPrompt').hide();
            });
        });
    </script>


    </body>
@endsection

