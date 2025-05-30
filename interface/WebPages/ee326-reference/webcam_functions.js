var websocket = null;
var localhost = "";
var b = document.getElementById('btnWS');
var buttonClicked = false;
var stamp = document.getElementById("timestamp");

// Initialize the websocket
function init() {
	if(window.location.hostname != "") {
		localhost = window.location.hostname;
	}

	doConnect();
}

function doConnect() { // makes a connection and defines callbacks
	if (b.innerText == "Start Webcam") {
		writeToScreen("Connecting to ws://" + localhost + ":81/ ...");
		b.disabled = true;
		//websocket = new WebSocket("ws://" + localhost + ":81/");
        websocket = new WebSocket("ws://localhost:81/ws");

		websocket.onopen = function(evt) {
			onOpen(evt)
		};
		websocket.onclose = function(evt) {
			onClose(evt)
		};
		websocket.onmessage = function(evt) {
			onMessage(evt)
		};
		websocket.onerror = function(evt) {
			onError(evt)
		};
	} else {
		writeToScreen("Disconnecting ...");
		websocket.close();
	}
}

function onOpen(evt) { // when handshake is complete:
	writeToScreen("Connected.");
	//*** Change the text of the button to read "Stop Webcam" ***//
  b.innerText = "Stop Webcam";

	//*** Change the title attribute of the button to display "Click to stop webcam" ***//
  b.title = "Click to stop webcam";
  

	//*** Enable the button ***//
  b.disabled = false;

	buttonClicked = false;
}

function onClose(evt) { // when socket is closed:
    writeToScreen("Disconnected. Error: " + evt);
    //*** Change the text of the button to read "Start Webcam" ***//
      b.innerText = "Start Webcam";

      //*** Change the title attribute of the button to display "Click to start webcam" ***//
      b.title = "Click to start webcam";    

      //*** Enable the button ***//
       b.disabled = false;
    
    
    // If the user never actually clicked the button to stop the webcam, reconnect.
	if (buttonClicked == false) {
		doConnect();
	}
	buttonClicked = false;
}

function onMessage(msg) {
	//*** Display a new timestamp ***//
    let time_ms = Date.now();
    let date = Date(time_ms);
	writeToScreen('New Image at: ' + date);
    stamp.innerText = date;
    
	
	// Get the image just taken from WiFi chip's RAM.
	var image = document.getElementById('image');
	var reader = new FileReader();
	reader.onload = function(e) {
		var img_test = new Image();
		img_test.onload = function(){image.src = e.target.result;};
		img_test.onerror = function(){;};
		img_test.src = e.target.result;
	};
	reader.readAsDataURL(msg.data);
}

function onError(evt) { // when an error occurs
	websocket.close();
	writeToScreen("Websocket error");
	
	//*** Change the text of the button to read "Start Webcam" ***//
  b.innerText = "Start Webcam";
  //*** Change the title attribute of the button to display "Click to start webcam" ***//
  b.title = "Click to start webcam";  
	
  //*** Enable the button ***//
	b.disabled = false;
	
	
	buttonClicked = false;
}

// Set up event listeners
b.addEventListener('click',onClick);
//*** When the button is clicked, disable it and set the 'buttonClicked' variable to true, and depending on whether a Websocket is open or not, either run "doConnect()" or "websocket.close()" ***//
function onClick() { // Our function that runs when button is clicked
    // Disable button
    b.disabled = true;
    
    
    // Set click var
    buttonClicked = true;
    
    // Run doConnect() if Websocket is closed or websocket.close() if opn
    if (b.innerText == "Start Webcam") {
        doConnect();
        b.style.backgroundColor = "skyblue";
    }
    else if (b.innerText == "Stop Webcam"){
        websocket.close();
        b.style.backgroundColor = "red";
    }
}


// Function to display to the message box
 function writeToScreen(message)
  {
	document.getElementById("msg").innerHTML += message + "\n";
	document.getElementById("msg").scrollTop = document.getElementById("msg").scrollHeight;
  }

// Open Websocket as soon as page loads
window.addEventListener("load", init, false);