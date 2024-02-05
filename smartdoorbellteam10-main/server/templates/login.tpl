<!DOCTYPE HTML>

<html lang="en">

<head>
	<meta charset="utf-8">

	<title>Smart Doorbell</title>
	<link rel="stylesheet" href="static/styles.css">
	<link rel="preconnect" href="https://fonts.gstatic.com">
	<link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">

	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">

</head>
<script>
	%include('loginscript.js')
</script>
<body>
	<!--
	TODO: Implement logic for adjusting title text
	-->
	<div class="body_container">
		<!--<div class="head_left"><h1>Smart Doorbell</h1></div>-->
		
	<div class="form_container">
		<img src="assets/LogoV1.png" class="logo">
			<div id="login_container">
				<form id="login_form" onsubmit="return submitUserCheck()">
					<div class="form_items">
						<label>Username</label>
						<input required title="The username you were provided." id="login_username" placeholder="doorbell_RaNdOMCh4Rs" name="username"/>
					</div>
					
					<div class="form_items init uninit" >
						<label>Password</label>
						<input  type=password placeholder="Password" name="password" />
					</div>
					
					<div class="form_items uninit" >
						<label>Email</label>
						<input placeholder="johndoe@mail.com" pattern=".+\@.+\..+" name="email" />
					</div>
					
					<button class="button" type="submit" form="login_form">Confirm</button>
				</form>
			</div>
			
			<div id="newuser_container">
				<h3 id="newuser_title" class="form_title">No Username?</h3>
				<form id="newuser_form" onsubmit="return submitNewUser()">
				<div class="form_items">
					<label>Doorbell ID</label>
					<input required title="A hyphen-separated identified found on your device." placeholder="12345678-abcd-abcd-123456789abc" name="uid" pattern="[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" />
				</div>
					<button class="button" type="submit" form="newuser_form">Confirm</button>
				</form>
			</div>
		</div>
	</div>

</body>
</html>

