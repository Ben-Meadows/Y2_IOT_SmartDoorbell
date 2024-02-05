function submitUserCheck(){
	let form = document.getElementById("login_form");
	fetch("username_check", {method:"post",body: new FormData(form)})
		.then(res => res.json())
		.then(data => {
			if (data.success){
				if(data.initialised){
					formInitialised()
				}
				else formUninitialised()
			}
		})
	return false;
}

function submitInitialisation(){
	let form = document.getElementById("login_form");
	fetch("initialise_user", {method:"post",body: new FormData(form)})
		.then(res => res.json()).then(res=>{
			if (res.success){
			submitLogin()
	}})	
	return false;
}

function submitLogin(){
	let form = document.getElementById("login_form");
	fetch("login", {method:"post",body: new FormData(form)})
		.then(res => res.json()).then(res=>{
			if(res.success){
				window.location.reload()
			}
		})
	return false;
}

function formUninitialised(){
	for (let elem of document.querySelectorAll(".uninit")){
		elem.style.display = "grid";
	}
	document.querySelector("#login_form").setAttribute("onsubmit","return submitInitialisation()");
	//document.querySelector("#login_title").innerText = "Please enter a password, and your email address";
}

function formInitialised(){
	document.querySelector("#login_form").setAttribute("onsubmit","return submitLogin()");
	for(let elem of document.querySelectorAll(".init"))
	{
		elem.style.display = "grid";
	}

}

function submitNewUser(){
	let form = document.getElementById("newuser_form");
	fetch("newuser", {method:"post", body:new FormData(form)})
		.then(res=>res.json()).then(data=>{document.getElementById("login_username").value = data.username; 
			console.log(data);
			if(data.success){formUninitialised()} else {formInitialised()}})
	return false;
}
