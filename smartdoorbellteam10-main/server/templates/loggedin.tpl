<!DOCTYPE HTML>

<html lang="en">

<head>
	<meta charset="utf-8">

	<title>Smart Doorbell</title>
	<link rel="stylesheet" href="static/styles.css">
	<link rel="preconnect" href="https://fonts.gstatic.com">
	<link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
	<link rel="preconnect" href="https://fonts.googleapis.com">

	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
	<script>
		% include('homescript.js')
	</script>
</head>

<body>
	<header>
	<!--<div class="head_left"><h1>Smart Doorbell</h1></div>-->
	<img class="header-image" src="assets/LogoV1.png">
	<button class="button" id="theme-swap">Change Theme</button>
	<div class="head_right">
		<h1 class="user_name">{{user.get("username")}}</h1> 
		<a href="/logout"><h1 class="button button2 logout">Logout</h1></a>
	</div>
	</header>
	
	<div class="containers">
		<div class="container" id="livefeed_container">
			<h1 class="title">Livefeed</h1>
			<img class="livefeed_frame" id="livefeed_frame" src="static/placeholder.png"/> <!--width=640 height=480-->
			<a id="livefeed_download"  download="placeholder.png" href="static/placeholder.png"><h1 class="button button2">Download</h1></a>
		</div>

		<div class="container-mid container">
			<h1 class="title">Snapshots</h1>
			<div id="snapshots_container">
				% for item in snapshots:
					<a download="{{item.get("name","")}}" href="data:image/jpg;base64,{{item.get("b64","")}}">
						<img class="snapshot_img" src="data:image/jpg;base64,{{item.get("b64", "")}}"/> <!--width=160 height=120-->
					</a>
				% end
			</div>
		</div>

		<div class="container">
			<h1 class="title">Recordings</h1>
			<div id="recordings_container">
				% for item in recordings[:4] if len(recordings) >=4 else recordings:
				<div class="recording_embed">
						<a class="recording_link" href="api/download/{{user.get("uuid")}}/{{item.get("name")}}">{{item.get("name", "Invalid name")}}</a>
						<video class="recording_vid" src="api/download/{{user.get("uuid")}}/{{item.get("name")}}" controls/>
				</div>
				% end
				% for item in recordings[4:] if len(recordings)>=4 else []:
				<div class="recording_noembed">
						<a class="recording_link" href="api/download/{{user.get("uuid")}}/{{item.get("name")}}">{{item.get("name", "Invalid name")}}</a>
				</div>
				%end
			</div>
		</div>
	<div>


	<script>

	let looper = window.setInterval(
		()=>newFrame(), 500
	)
	async function newFrame(){
		let res = await fetch('api/livefeed/latest');
		res = await res.json();
		if(res.success){
let content=res;
			clearInterval(looper);
			looper = window.setInterval(()=>newFrame(),500);
			document.getElementById("livefeed_frame").setAttribute("src", `data:image/jpg; base64,${content.image}`);
			document.getElementById("livefeed_download").setAttribute("href", `data:image/jpg; base64,${content.image}`);
			document.getElementById("livefeed_download").setAttribute("download", `${content.name}`)
		}
		else{	
			clearInterval(looper);
			looper = window.setInterval(()=>newFrame(), 2000);
	}
	}
	</script>
	<script>
		% include('theme.js')
	</script>
</body>
</html>
