<!DOCTYPE html>
<html>
	<head>
		<title>{{ $page_title or config('app.app_name'). " EDUGraphApi" }}</title>
		@yield('before.css')
		<link rel="stylesheet" href="{{ asset('/css/bootstrap.min.css') }}">
		<link rel="stylesheet" href="https://appsforoffice.microsoft.com/fabric/1.0/fabric.css">
		<link rel="stylesheet" href="https://appsforoffice.microsoft.com/fabric/1.0/fabric.components.css">
		<link rel="stylesheet" href="{{ asset('/css/app.css') }}">
		@yield('after.css')
	</head>
	<body class="ms-Grid">
		<div class="content">
			<div class="ms-Grid">
				<div class="ms-Grid-row">
					<div class="ms-NavBar">
						<ul class="ms-NavBar-items">
							<li class="navbar-header">
								Edu Demo App
							</li>
						</ul>
					</div>
					<div class="ms-Grid-col ms-u-mdPush1 ms-u-md9 ms-u-lgPush1 ms-u-lg6">
						@yield('content')
					</div>
				</div>
			</div>
		</div>
	</body>

	<script src="{{ asset('js/jQuery-2.2.0.min.js') }}"></script>
	@yield('after.js')
</html>