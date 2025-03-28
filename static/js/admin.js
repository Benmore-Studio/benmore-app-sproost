  console.log(csrfToken, userId, "try");

  let header = document.querySelector("#header")
  let userTools = document.querySelector("#user-tools")
  let chatIcon = document.querySelector("#chat-icon")
  let iconContainer = document.querySelector("#icon-container")
  let openModalBtn = document.querySelector("#openModalBtn")
  const chatContainer = document.getElementById("chatList");
  const ChatList = document.getElementById("chatList");
  const individualChatListBody = document.getElementById("individual-chatList-body");
  const backArrow = document.getElementById("back-arrow");
  const personalMessageBackArrow  = document.getElementById("personal-back-arrow")
  const addUserToGroup = document.getElementById("add-user");
  const adminleaveRoomButton = document.getElementById("leave-room");
  const adminDeleteRoomButton = document.getElementById("delete-room");
  const leaveRoomYesOrNoModal = document.getElementById("leave-room-yes-or-no-modal");
  const deleteRoomYesOrNoModal = document.getElementById("delete-room-yes-or-no-modal");
  const removeUserYesOrNoModal = document.getElementById("remove-user-yes-or-no-modal");
  let mainBody = document.getElementById('main-body')
  let createChatModal = document.getElementById('create-chatModal')
  let addUserModal = document.getElementById("only-add-user-modal")
  let leaveRoomCloseModalBtn = document.getElementById("leave-room-closeModalBtn")
  let removeUserCloseModalBtn = document.getElementById("remove-user-closeModalBtn")
  let leaveRoomConfirm = document.getElementById("leave-room-confirm")
  let removeUserConfirm = document.getElementById("remove-user-confirm")
  let deleteRoomConfirm = document.getElementById("delete-room-confirm")
  let deleteRoomCloseModalBtn = document.getElementById("delete-room-closeModalBtn")
  let deleteUserConfirm = document.getElementById("delete-user-confirm")
  let replyMessageCancel = document.getElementById("reply-message-cancel")
  let cancelMediaView = document.getElementById("cancel-media-view")
  let groupChat = document.getElementById("group-chat")
  let grouindividualGroupParentsChat = document.getElementById("individual-group-parents")
  let messageBodyParent = document.getElementById("message-body-parent")
  let personalMessageBodyParent = document.getElementById("personal-message-body-parent")
  let groupMessageBackArrow = document.getElementById("group-message-back-arrow")

  if(backArrow){
    backArrow.style.marginTop = '8px'

  }
  // to store room roomDetails, especially id
  const roomDetails = {}
  let replyMessageId;
  let user_room_types;
  let globalSearchId;
  let globalRoomName;
  let adminAddUserRoomTitle;
  let roomMembers;
  let sender ;
  let dontUpdateMessageNumber = false;
  let dontUpdatePrivateMessageNumber = false;
  let messageCount = 0
  let globalMessageheight = false
  let prependMode = false;
  let scrollFromBottom;
  let globalMessageScroll;
  let uploadedMedia = []; 
  const maxFiles = 3;
  let globalPublicId = {};


  groupChat.addEventListener("click", ()=>{
    console.log("all-individual-groups");
    document.getElementById("group-message-page").style.display = "block"
    mainBody.style.display = "none"
    grouindividualGroupParentsChat.style.display = "block"
    personalMessageBodyParent.style.display = "block"
  })


  cancelMediaView.addEventListener("click", ()=>{
    document.getElementById("view-chat-media").style.display = "none"
    document.getElementById("chat-media").innerHTML = ""
  })

  // toggle chat body
  header.prepend(iconContainer)
  function toggleChatDropdown() {
    const dropdown = document.getElementById('chatDropdown');
    dropdown.classList.toggle('hidden');
  }

  // WebSocket setup
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  
  
  const chatSocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/chat/");
  let currentRoomId = null;
  let currentPage = 1;
  let isLoading = false;

  groupMessageBackArrow.addEventListener("click", function(){
    grouindividualGroupParentsChat.style.display = 'none'
    mainBody.style.display = 'block'

  })
  backArrow.addEventListener("click", function(){
    const searchNavigation= document.getElementById("search-navigation")
    if(searchNavigation){
      searchNavigation.style.display="none"
    }
    grouindividualGroupParentsChat.style.display = 'block'
    messageBodyParent.style.display = 'none'
    dontUpdateMessageNumber = false
    document.getElementById('chat-message-parent-div').style.display = 'none'

  })




  function openChatRoom(roomId, messages, type, roomName, searchId) {
    console.log("typppqwe", type, roomName);
    if(type == "search"){
      document.getElementById("message-search-results").style.display = "none"

      let nextSearchResult = document.createElement("div")
      let previousSearchResult = document.createElement("div")
      nextSearchResult.innerHTML = `<button onclick="highlightSearchResult(currentSearchIndex + 1)">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4 text-black">
                                      <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
                                    </svg>
                                  </button>`
      previousSearchResult.innerHTML = `<button onclick="highlightSearchResult(currentSearchIndex - 1)">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4 text-black">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                </svg>             
              </button> ` 
    const searchNavigation = document.getElementById("search-navigation") 
    searchNavigation.innerHTML = ""   
    searchNavigation.appendChild(nextSearchResult)
    searchNavigation.appendChild(previousSearchResult)                 
    }     

    if(type === "private"){
      dontUpdatePrivateMessageNumber = true
      mainBody.style.display = "none"
      personalMessageBodyParent.style.cssText = "display:flex; flex-direction:column;"
    }
    console.log("opened", "chat");
    if(type == "message"){
      dontUpdateMessageNumber = true
      messageBodyParent.style.display = "block"
      grouindividualGroupParentsChat.style.display = "none"
      const messageNumberElement  = document.querySelector(`#messageNumber-${roomId}`);
      messageNumberElement.innerHTML = ''
      messageNumberElement.style.opacity = 0
      console.log("messageNumberElement",messageNumberElement);

    }
    currentRoomId = roomId;
    currentPage = 1;
    document.getElementById('message-body').innerHTML = ''
    document.getElementById('chat-message-parent-div').style.display = 'block'
    chatContainer.style.display = 'none'
    const roomTitle = document.getElementById("roomTitle")
    roomTitle.innerHTML = roomName
    globalRoomName = roomName
    roomTitle.style.textAlign = 'center'
    ChatList.style.display = 'block'
    ChatList.style.color = 'black'

    // Request first batch of messages
    chatSocket.send(JSON.stringify({
        action: "load_messages",
        room_id: roomId,
        page: currentPage
    }));

    if(type === "search"){
      // Store search matches for navigation
      currentSearchIndex = 0;

      // Highlight first match
      setTimeout(() => highlightSearchResult(0, searchId), 1000);
    }
}


//#region   message search

let searchResults = [];  // Store found messages
let currentSearchIndex = -1;  // Track highlighted message index


// let searchArrowButton = document.getElementById("searchBackArrow")
// console.log("cry", searchArrowButton);
// if(searchArrowButton){
  
// }

// chatroom async chat
async function searchMessages() {
    const query = document.getElementById("messageSearchInput").value.trim();
    chatList.style.display = "none"
    if (!query) {
      document.getElementById("searchResults").innerHTML = "";  
      searchResults = [];
      currentSearchIndex = -1;
      return;
    }

    const csrfToken = getCookie('csrftoken');  

    const response = await fetch(`/chat/search_messages/?q=${query}`, {
      method: "GET",
      headers: {
        "X-CSRFToken": csrfToken,  
        "Content-Type": "application/json"
      },
      credentials: "include"
    });

    const data = await response.json();
    
    if (data.error) {
      console.error(data.error);
      return;
    }


    console.log("dd", data);

    const resultsDiv = document.getElementById("message-search-results");
    const chatList = document.getElementById("chatList")
    let searchBackArrow = document.createElement("div")
    searchBackArrow.setAttribute("id", 'searchBackArrow')
    searchBackArrow.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4 cursor-pointer text-black">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
                                </svg>
                                `
    searchBackArrow.addEventListener("click", function(){
      // document.getElementById("search-navigation").style.display = "none"
      console.log("must", searchBackArrow);
      resultsDiv.style.display = "none"
      chatList.style.display = "block";

    })
    // resultsDiv.className = ""
    resultsDiv.innerHTML = "";
    resultsDiv.appendChild(searchBackArrow)

    searchResults = data.results;  
    currentSearchIndex = -1;

    if (data.results.length > 0) {
      chatList.style.display = "none";
        resultsDiv.style.display = "block";
        

        data.results.forEach((room, index) => {
          console.log("search", data.results, index);
          const roomElement = document.createElement("div");
          roomElement.setAttribute('data-search-id', index)
          roomElement.classList.add("p-2", "border-b", "cursor-pointer", "hover:bg-gray-200", "text-black");
          roomElement.innerHTML = `<strong>${room.room_name}</strong> (${room.messages.length} matches)`;
          
          // Click to open the room and highlight the first matching message
          roomElement.addEventListener("click", (event) => {
              const searchId = event.currentTarget.getAttribute("data-search-id");
              console.log("Clicked element's search ID:", searchId);
              globalSearchId = searchId

              const openChatType = "search";
              // Call the openChatRoom function with correct arguments
              openChatRoom(room.room_id, room.content, openChatType, room.room_name, searchId);
          });
          resultsDiv.appendChild(roomElement);
        });
    }else{
      chatList.style.display = "none";
        resultsDiv.style.display = "block";
      let noResult = document.createElement("p")
      noResult.innerHTML = "No result found"
      noResult.style.color = "black"
      resultsDiv.appendChild(noResult)
    }

  }


function highlightSearchResult(index, searchId) {
  console.log("much", searchId);
  
  if (!searchResults || searchResults.length === 0) {
    console.warn("No search results available.");
    return;
    }

  console.log("Valid index:", index);
  console.log("Search Results:", searchResults);
  console.log("Current Room:", searchResults[globalSearchId]);
  let room = searchResults[globalSearchId];  // Get the chat room object
  if (!room || !room.messages || room.messages.length === 0 || index >= room.messages.length || index < 0) {
    console.warn("No messages found for this room.");
    return;
  }

  console.log(index, searchResults.length,searchResults[index]);
 
  console.log("trouble", searchResults[globalSearchId].messages);
  currentSearchIndex = index;
  let messageId = searchResults[globalSearchId].messages[index].id;
  
    // Find the message in chat and highlight it
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    console.log("ache",searchResults);
    if (messageElement) {
      console.log("scroll", messageElement);
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

      messageElement.style.transition = "background-color 2s ease";
      messageElement.style.backgroundColor = "yellow";

      setTimeout(() => {
          messageElement.style.backgroundColor = "";
      }, 3000);
    }
}


document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowUp") {
        ;
    } else if (event.key === "ArrowDown") {
        highlightSearchResult(currentSearchIndex + 1);
    }
});



document.getElementById("messageSearchInput").addEventListener("input", searchMessages);

//#endregion



function loadChatRoom(roomId) {
    console.log(`Loading chat room: ${roomId}`);

    // Show the chat panel
    ChatList.style.display = "block";

    // Set the room title
    document.getElementById("roomTitle").innerText = `Chat Room ${roomId}`;

    // Clear previous messages
    const chatMessages = document.getElementById("message-body");
    chatMessages.innerHTML = "Loading messages...";

    // Fetch and display messages
    fetch(`/get-messages/?room_id=${roomId}`)
        .then(response => response.json())
        .then(data => {
            chatMessages.innerHTML = "";  // Clear loading text

            data.messages.forEach(msg => {
                const msgDiv = document.createElement("div");
                msgDiv.id = `message-${msg.id}`;  // Set unique ID for highlighting
                msgDiv.classList.add("p-2", "border-b");

                // Message structure
                msgDiv.innerHTML = `
                    <div class="flex gap-4">
                        <p class="text-[#417690] font-bold">${msg.sender}</p>
                        <p class="text-gray-300 text-sm">${msg.timestamp}</p>
                    </div>
                    <p>${msg.content}</p>
                `;

                chatMessages.appendChild(msgDiv);
            });

            console.log("Messages loaded successfully.");
        })
        .catch(error => {
            console.error("Error loading chat messages:", error);
            chatMessages.innerHTML = "Failed to load messages.";
        });
}




// Navigate between search results
function nextSearchResult(roomId) {
    if (searchResults.length > 0) {
        highlightSearchResult(roomId, currentSearchIndex + 1);
    }
}

function previousSearchResult(roomId) {
    if (searchResults.length > 0) {
        highlightSearchResult(roomId, currentSearchIndex - 1);
    }
}

  chatSocket.onopen = () => {
    console.log("WebSocket connection established");
  };


  function createMessageElement(msg) {
  const div = document.createElement("div");
  div.classList.add("chat-message"); // Use your actual styling class

  // Customize based on your message structure
  div.innerHTML = `
    <div class="text-sm text-gray-800 font-semibold">${msg.username}</div>
    <div class="text-sm text-gray-600">${msg.message}</div>
    <div class="text-xs text-gray-400">${msg.timestamp}</div>
  `;

  return div;
}





  chatSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log("call",data, userId);
    if (data.action === "room_list") {
      updateChatRooms(data);  // Update the chat room UI
      document.getElementById("all-chatroom-loader-modal").style.display ="none"
      ChatList.style.display ="block"

    } 
    else if (data.action === "new_room") {
      updateChatRooms(data);  // Update the chat room UI
    } 
    else if (data.action === 'typing') {
      console.log(data);
      let roomId = `chat-room-${data.room}`
      let room = document.getElementById(roomId)
      let typingDiv = document.getElementById('typing-div')
      if(data.typing === true){
        if(data.username !== userId){
          document.getElementById("suggestion-div").style.display = "block"
          typingDiv.innerHTML = `${data.username} is typing` 
          typingDiv.className = "text-green-500 text-sm mb-3 float-left"
          typingDiv.style.cssText = "text-transform: none; font-family: Rubik, sans-serif; font-size: 13px;"      
        }
        room.children[3].innerHTML = `${data.username} is typing`
        room.children[3].className = "text-green-500 text-sm"
       
        room.children[1].style.display = "none"
        console.log(room.children[1], room.children[2], "room.children[1]");
        room.children[2].style.display = "none"
        room.children[3].style.cssText = "text-transform: none; font-family: Rubik, sans-serif; font-size: 13px;"
      
      }else{
        
        room.children[1].style.display = "block"
        room.children[2].style.display = "block"
        room.children[3].style.display = "none"
        // document.getElementById("suggestion-div").style.display = "none"
        typingDiv.style.display = "none"
    
      }
    }
    else if (data.action === "message") { 
      console.log("uphreme", data);
      let iconString = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-3 text-gray-500 cursor-pointer">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /> onClick="openOptions()"
                       </svg>`
      updateChatList(data.room, data.message, data.timestamp, data.sender )
      const formattedText = formatMessage(data.message);
      console.log("wwww", data.message);
      const chatMessages = document.getElementById('message-body');   
      const msgDiv = document.createElement('div');
      const icon = document.createElement('div');
      const messageOptions = document.createElement('div');
      const iconUsernameAndDate = document.createElement('div');
      const replyMessage = document.createElement('p');
      const deleteMessage = document.createElement('p');
      const highlightMessage = document.createElement('p');

      replyMessage.innerHTML = "reply";
      deleteMessage.innerHTML = "delete";
      highlightMessage.innerHTML = "highlight";


       //  Setting their ids and event listeners
      replyMessage.setAttribute("data-id", data.message_id);
      replyMessage.addEventListener("click", (e) => {
        replyMessageId = e.currentTarget.getAttribute("data-id");
        const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
        console.log(data.message_id, "data-id", messageElement);
        const replyMessageDiv = document.getElementById("reply-message-div")
        const messageInput = document.getElementById("message")
        messageInput.focus()
        const gottenReplyMessageUsername= e.target.parentElement.parentElement;
        const replyMessageUsername= document.createElement('p');
        replyMessageUsername.className = "text-green-800"
        const replyMessageContent = document.createElement('p');
        if (messageElement) {
          replyMessageContent.textContent = messageElement.textContent;
          replyMessageContent.className = "text-black"
          console.log("Message text:", messageElement.textContent);
        } else {
          replyMessageContent.textContent = "--";
        }
        
        replyMessageUsername.textContent = gottenReplyMessageUsername.previousSibling.children[0].textContent
        replyMessageDiv.style.display = "block"
        replyMessageDiv.children[0].append(replyMessageUsername)
        replyMessageDiv.children[0].append(replyMessageContent)
        document.getElementById("suggestion-div").style.display = "block";

        
        e.target.parentElement.style.display = "none"
        console.log("e.target.parentElement", e.target.parentElement);
      });
      
      deleteMessage.setAttribute("data-delete-id", data.message_id);
      deleteMessage.addEventListener("click", (e)=>{
        console.log("deleteWW",e.target);
        e.target.parentElement.style.display = "none"
        console.log("checkinggg", e.target.parentElement);
        chatSocket.send(JSON.stringify({
            action: "delete",
            message_id: data.message_id
        }));

      })




      messageOptions.className = "message-options flex-col gap-4 bg-white w-fit absolute w-fit p-3 bottom-[-1rem] right-4";
      messageOptions.style.display = "none"
      replyMessage.className = "cursor-pointer text-black hover:bg-gray-100 p-2";
      deleteMessage.className = "cursor-pointer text-black hover:bg-gray-100 p-2";
      highlightMessage.className = "cursor-pointer text-black hover:bg-gray-100 p-2";
      
      
      const messageBody = document.createElement('div');
      messageBody.setAttribute("data-message-id", data.message_id)
      icon.innerHTML = iconString;
      const usernameAndDate = document.createElement('div');
      messageBody.style.textTransform = "none"; 
      messageBody.style.fontFamily = "'Rubik', sans-serif";
      messageBody.style.fontSize = "13px";
      const msgDivDate = document.createElement('p');
      const msgDivUsername = document.createElement('p');
      msgDivDate.textContent = data.timestamp;
      msgDivUsername.textContent = data.username;

      // designing the message div
      const mainMessageContent = document.createElement('p');
      const replyMsgDiv = document.createElement('div');
      mainMessageContent.textContent = formattedText;
      mainMessageContent.style.textAlign = "start"

      // attaching  media if any
      if(data.media.length > 0){
        const wrapper = document.createElement("div");
        console.log("clg", data.media);
        if(data.media.length > 2){
          wrapper.className = "image-message-parent w-fit grid grid-cols-2"
        }else{
          wrapper.className = "image-message-parent w-fit flex gap-[4px]"

        }
        for (const item of data.media) {
          console.log("item", item);

          const mediaElement = document.createElement("div");
          mediaElement.setAttribute("id", item.public_id);
          mediaElement.className = "w-fit";
          if (item.type === "video") {
            mediaElement.innerHTML = `<video src="${item.url}" width="180" controls></video>`;
          } else if (item.type === "image") {
            mediaElement.innerHTML = `<img src="${item.url}" width="180">`;
          }

          wrapper.append(mediaElement);
        }
        mainMessageContent.append(wrapper)
      }

      


      // if a user is replying a message
      if(data.reply_to_content !== "None" && data.reply_to_id !== null){     
        replyMsgDiv.innerHTML= `
        <div style="text-align: start;">
          <div class="w-full flex flex-col gap-4 bg-gray-200 text-gray-600 text-transform-none border-l-2 border-green-200 p-4 rounded-t-md mb-1" onClick="findRepliedMessage(${data.reply_to_id})">
          <p class="text-black">${data.sender}</p>
          <p>${data.reply_to_content}</p>
          </div>
        </div> `
          messageBody.appendChild(replyMsgDiv)
          messageBody.appendChild(mainMessageContent)      
      }else{
          messageBody.appendChild(mainMessageContent);
      }
      

      msgDiv.className = "bg-gray-100 p-2 rounded mb-2 relative";
      msgDivUsername.className = "text-[#417690] text-bold";
      msgDivDate.className = "text-gray-300 text-small";
      messageBody.className = "justify-self-start";
      iconUsernameAndDate.className = "flex justify-between";
      usernameAndDate.className = "flex gap-4";

      // appending the messageoptions
      messageOptions.appendChild(replyMessage)
      messageOptions.appendChild(deleteMessage)
      messageOptions.appendChild(highlightMessage)
      icon.appendChild(messageOptions)
      icon.addEventListener("click", (e)=>openOptions(e))
      usernameAndDate.appendChild(msgDivUsername)
      usernameAndDate.appendChild(msgDivDate)
      iconUsernameAndDate.prepend(usernameAndDate)
      iconUsernameAndDate.appendChild(icon)
      msgDiv.prepend(iconUsernameAndDate)
      msgDiv.append(messageBody)
      if(data.room_type === "group_chat"){
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
      else if(data.room_type === "private"){
        personalMessageBodyParent.appendChild(msgDiv);
        personalMessageBodyParent.scrollTop = chatMessages.scrollHeight;
      }
    }
    
    // else if (data.action === "message_list") {
    //   const chatMessages = document.getElementById('message-body');
    //   const scrollFromBottom = chatMessages.scrollHeight - chatMessages.scrollTop;

    //   if (globalMessageScroll === 0 && data.messages.length < 1){
    //     return
    //   }
    //   if (prependMode) {
    //     data.messages.forEach(msg => addMessage(msg.username, msg.deleted, msg.message, msg.timestamp, msg.id, msg.username, msg.reply_to, msg.reply_to_num, msg.url));
    //     isLoading = false;
    //     roomMembers = data.members
    //     // scroll offset fix
    //     requestAnimationFrame(() => {
    //       chatMessages.scrollTop = chatMessages.scrollHeight - scrollFromBottom;
    //       isLoading = false;
    //     });

    //     prependMode = false;
    //     return;

    //   }else{    
        
    //   console.log("wooo", data);

    //   chatMessages.innerHTML = "";
    //   // chatMessages.style.height = "60%"
    //   // Reverse messages (oldest first) and add to chat
    //   data.messages.reverse().forEach(msg => {addMessage(msg.username, msg.deleted, msg.message, msg.timestamp, msg.id, msg.username, msg.reply_to, msg.reply_to_num, msg.media)});
    //   isLoading = false;
    //   roomMembers = data.members
    //   // scroll to the bottom
    //   setTimeout(() => {
    //     chatMessages.scrollTop = chatMessages.scrollHeight;
    // }, 100);
    // }
    //   document.getElementById("individual-chatroom-modal").style.display ="none"
    //   document.getElementById("message-body").style.width ="100%"
    //   individualChatListBody.style.display ="flex"
    // } 


    else if (data.action === "message_list") {
      const chatMessages = document.getElementById('message-body');
        const scrollFromBottom = chatMessages.scrollHeight - chatMessages.scrollTop;
  
        if (globalMessageScroll === 0 && data.messages.length < 1){
          return
        }
        if (prependMode) {
          console.log("first", data);
          data.messages.forEach(msg => addMessage(msg.username, msg.deleted, msg.message, msg.timestamp, msg.id, msg.username, msg.reply_to, msg.reply_to_num, msg.media));
          isLoading = false;
          roomMembers = data.members
          // scroll offset fix
          requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight - scrollFromBottom;
            isLoading = false;
          });
  
          prependMode = false;
          return;
      }
      else {    
        console.log("wooo", data);
    
        chatMessages.innerHTML = "";
        // Reverse messages (oldest first) and add to chat
        data.messages.reverse().forEach(msg => {addMessage(msg.username, msg.deleted, msg.message, msg.timestamp, msg.id, msg.username, msg.reply_to, msg.reply_to_num, msg.media)});
        isLoading = false;
        roomMembers = data.members
          // scroll to the bottom
          setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
          document.getElementById("individual-chatroom-modal").style.display ="none"
          document.getElementById("personal-chatroom-modal").style.display ="none"
          document.getElementById("message-body").style.width ="100%"
          individualChatListBody.style.display ="flex"
        } 
      }    
    
    else if(data.action === "missed_messages"){
      console.log("data.missed_messages", data.missed_messages);
      data.missed_messages.forEach(keyStr => {
        const keys = Object.keys(keyStr);
        console.log("keyStr", keys, keyStr, keyStr[keys[0]])
        const messageNumberElement  = document.querySelector(`#messageNumber-${keys[0]}`);
        console.log(messageNumberElement);
        let messageNumber = messageNumberElement.textContent
        console.log(messageNumber !== "", messageNumber);
        if(messageNumber !== ""){
          messageNumberElement.textContent = Number(messageNumber) + Number(keyStr[keys[0]])
          if(Number(messageNumberElement.textContent)>0){
            messageNumberElement.style.opacity = 1
          }
        }else{
          messageNumberElement.textContent = Number(keyStr[keys[0]])
          if(Number(messageNumberElement.textContent)>0){
            messageNumberElement.style.opacity = 1
            console.log("mmmm");
          }
        }
        
      });
      document.getElementById("all-chatroom-loader-modal").style.display ="none"
      document.getElementById("chatroom-load").style.display ="block"
    }
    else if(data.action === "message_deleted"){
      console.log("delete", data);
      const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
      // messageElement.parentElement.style.display = "none"
      console.log("don",messageElement);
      messageElement.innerHTML = ""
      messageElement.innerHTML = "This message has been deleted"
      messageElement.className ="text-red-500 justify-self-start"
      // messageElement.parentElement.parentElement.parentElement.parentElement.children[1].innerHTML = ""
      // messageElement.parentElement.parentElement.parentElement.parentElement.children[1].innerHTML = "This message has been deleted"
      // console.log("juuju",messageElement.parentElement.parentElement.parentElement.parentElement);
      // messageElement.parentElement.parentElement.parentElement.parentElement.children[1].className ="text-red-500 justify-self-start"
    }
    else if(data.action === "user_status"){
      renderOnlineStatus(data.user_id,  data.status, data.username, data.room_id, data.room_name)
    }
};



function findRepliedMessage(messageId) {
  const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
  if (messageElement) {
    const container = messageElement.parentElement;
    // Apply a transition so the background color change is smooth.
    container.style.transition = "background-color 2s ease";
    // Set the background to yellow.
    container.style.backgroundColor = "lemon";
    // Scroll the element into view.
    messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    // After 3 seconds, remove the yellow background.
    setTimeout(() => {
      container.style.backgroundColor = "";
    }, 3000);
  }
}



  chatSocket.onerror = function(e) {
    console.error("WebSocket encountered an error:", e);
  };

  chatSocket.onclose = (error) => {
    console.log("WebSocket connection closed", error);
  };


 // Stores uploaded media references



//  document.getElementById("mediaPreview").addEventListener("click", async function (e) {
//   console.log("delegation");
//   if (e.target.classList.contains("remove-btn")) {
//     const mediaElement = e.target.closest("[data-media-id]");
//     const mediaId = mediaElement?.dataset?.mediaId;

//     if (!mediaId) return;

//     mediaElement.remove();
//     uploadedMedia = uploadedMedia.filter(m => m.id !== mediaId || m.public_id !== mediaId);

//     document.getElementById("mediaInput").value = "";
//     if (uploadedMedia.length < 3) {
//       document.getElementById("chat-message-submit").firstElementChild.disabled = false;
//     }

//     try {
//       await fetch(`/delete_media/${mediaId}/`, { method: "DELETE" });
//     } catch (err) {
//       console.warn("Cloudinary delete failed:", err);
//     }
//   }
// });



async function removeMedia(publicId) {
  // 1. Remove from the preview DOM
  const mediaElement = document.querySelector(`[data-media-id="${publicId}"]`);
  if (mediaElement) {
    mediaElement.remove();
  }

  // 2. Remove from uploadedMedia array
  uploadedMedia = uploadedMedia.filter(media => media.public_id !== publicId);

  // 3. Optionally reset the file input so the user can select again
  document.getElementById("mediaInput").value = "";

  // 4. Optionally re-enable the submit button if under the limit
  if (uploadedMedia.length < 3) {
    document.getElementById("chat-message-submit").firstElementChild.disabled = false;
  }

  // 5. Send delete request to backend
  console.log(globalPublicId);
  try {
    const csrftoken = getCookie("csrftoken");
    const response = await fetch(`/chat/delete_media/${globalPublicId[publicId]}/`, { method: "DELETE",  headers: {
    'X-CSRFToken': csrftoken
  } });
    if (!response.ok) {
      console.warn(`Failed to delete media from Cloudinary: ${publicId}`);
    }
  } catch (error) {
    console.error(`Error deleting media ${publicId}:`, error);
  }
}


  
// function displayMediaPreview(url, publicId) {
//   console.log("baby");
//     document.getElementById("suggestion-div").style.display = "block";
//     const previewContainer = document.getElementById("mediaPreview");
//     previewContainer.style.display = 'block'
//     const mediaElement = document.createElement("div");
//     mediaElement.setAttribute("data-media-id", publicId);
//     mediaElement.className = "w-fit"
//     if (url.startsWith("data:video")) { // Detect video files
//         mediaElement.innerHTML = `<button class="cursor-pointer text-red-500 text-md font-lg" onclick="removeMedia('${publicId}')">X</button> <video src="${url}" width="180" controls></video>`;
//     } else { // Assume it's an image
//         mediaElement.innerHTML = `<button class="cursor-pointer text-red-500 text-md font-lg" onclick="removeMedia('${publicId}')">X</button> <img src="${url}" width="180">`;
//     }

//     previewContainer.appendChild(mediaElement);
// }



// Attach event listener to file input
// document.getElementById("mediaInput").addEventListener("change", handleFileSelect);



document.getElementById("mediaInput").addEventListener("change", async (event) => {
  console.log("object");
  const rawFiles = Array.from(event.target.files);
  const files = rawFiles.slice(0, maxFiles);

  console.log("fffii", files, rawFiles.length);
  if (!files.length) return;

  uploadedMedia = []; // Reset
  const previewContainer = document.getElementById("mediaPreview");
  previewContainer.innerHTML = "";

  document.getElementById("chat-message-submit").firstElementChild.disabled = true;

  console.log("llll",files.length)

  for (let i = 0; i < files.length; i++) {
    console.log("max", i);
    const file = files[i];
    const reader = new FileReader();

    reader.onload = function (e) {
      displayMediaPreview(e.target.result, i, files.length);
    };
    reader.readAsDataURL(file);

    try {
      const csrftoken = getCookie("csrftoken");
      const response = await fetch("/chat/cloudinary-signature/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ fileName: file.name }),
      });

      const data = await response.json();
      const { signature, timestamp, api_key, cloud_name } = data;

      const formData = new FormData();
      formData.append("file", file);
      formData.append("cloud_name", cloud_name);
      formData.append("timestamp", timestamp);
      formData.append("signature", signature);
      formData.append("api_key", api_key);

      await uploadMedia(file, formData, i, data);
      console.log((i));
    } catch (err) {
      console.error("Upload error:", err);
    }
  }

  if(rawFiles.length > 3){
      Toastify({
          text: "Sorry! max 3 files",
          duration: 3000, // Time in milliseconds (3 seconds)
          close: true, // Show close button
          gravity: "top", // `top` or `bottom`
          position: "right", // `left`, `center`, or `right`
          backgroundColor: "linear-gradient(to right, #ff4d4d, #ff0000)",
      }).showToast();
    }

  document.getElementById("chat-message-submit").firstElementChild.disabled = false;
  document.getElementById("mediaInput").value = "";
});



function displayMediaPreview(url, index, total) {
  const container = document.getElementById("mediaPreview");
  document.getElementById("suggestion-div").style.display = "block";
  container.style.display = "flex";
  container.style.gap = "1rem";

  const size = total <= 2 ? "230px" : "150px";

  const wrapper = document.createElement("div");
  wrapper.setAttribute("data-media-id", index);
  wrapper.className = "w-fit relative";

  if (url.startsWith("data:video")) {
    wrapper.innerHTML = `
    <button class="cursor-pointer text-red-500 text-md font-lg" onclick="removeMedia('${index}')">X</button>
      <video src="${url}" width="${size}" controls class="rounded shadow-md"></video>
    `;
  } else {
    wrapper.innerHTML = `
    <button class="cursor-pointer text-red-500 text-md font-lg" onclick="removeMedia('${index}')">X</button>
      <img src="${url}" width="${size}" class="rounded shadow-md" />
    `;
  }

  container.appendChild(wrapper);
  document.getElementById("message").focus()
}


async function uploadMedia(file, formData, numKey, data) {
  console.log("ded",data);
  const { signature, timestamp, api_key, cloud_name } = data;
  const cloudinaryUrl = `https://api.cloudinary.com/v1_1/${cloud_name}/auto/upload`;
  const uploadResponse = await fetch(cloudinaryUrl, {
    method: "POST",
    body: formData,
  });

  const uploadResult = await uploadResponse.json();
  const extension = file.name.split(".").pop().toLowerCase();

  let type = "file";
  if (file.type.startsWith("image/") || ["jpg", "jpeg", "png", "webp", "gif"].includes(extension)) {
    type = "image";
  } else if (file.type.startsWith("video/") || ["mp4", "mov", "avi"].includes(extension)) {
    type = "video";
  }

  uploadedMedia.push({
    url: uploadResult.secure_url,
    public_id: uploadResult.public_id,
    type: type,
  });

  globalPublicId = {[numKey]: uploadResult.public_id}
  console.log(globalPublicId);
}




function sendMessage() {
  const input = document.getElementById('message');
  const message = input.value.trim();

  // Prevent sending if there's no text and no media
  if (!message && (!uploadedMedia || uploadedMedia.length === 0)) return;

  // Ensure WebSocket is open before sending a message
  if (chatSocket.readyState === WebSocket.OPEN) {
    // Build the payload
    const payload = {
      action: "send",
      room_id: roomDetails[globalRoomName],
      message: message,
      receiver: roomMembers,
      room_type:user_room_types 
    };

    // If replying, attach the reply message ID
    if (replyMessageId) {
      payload.reply_to_id = replyMessageId;
    }

    // If there are any attached media, include them in the payload
    if (uploadedMedia && uploadedMedia.length > 0) {
      payload.media = uploadedMedia;
    }

    console.log("payload", payload, user_room_types);
    chatSocket.send(JSON.stringify(payload));

    // Hide the suggestion div for mentions (if present)
    const replyMessageDiv = document.getElementById("reply-message-div");
    const mentionDiv = document.getElementById("reply-message-div");
    if (replyMessageId && replyMessageDiv) {
      console.log("suggestionDiv");
      replyMessageDiv.style.display = "none";
    }
    if (mentionDiv) {
      mentionDiv.style.display = "none";
    }

    // If there's a reply UI active, remove its extra elements
    const cancelButton = document.getElementById("reply-message-cancel");
    if (cancelButton) {
      // Example logic: remove two sibling elements after the cancel button
      let firstSibling = cancelButton.nextSibling ? cancelButton.nextSibling.nextSibling : null;
      let secondSibling = firstSibling && firstSibling.nextSibling ? firstSibling.nextSibling : null;
      if (firstSibling) firstSibling.remove();
      if (secondSibling) secondSibling.remove();
      
    }

    // Clear the text input and reset the attached media (if applicable)
    input.value = '';
    document.getElementById("mediaPreview").innerHTML = ""; // Clear media preview
    uploadedMedia = []; // Clear media attachments after sending
    // Optionally, also clear replyMessageId if needed:
    replyMessageId = null;
  } else {
    console.error("WebSocket is not open. Cannot send message.");
  }
}


  // Start typing
function onInputChange() {
  const inputEl = document.getElementById('message');
  const inputValue = inputEl.value;
  chatSocket.send(JSON.stringify({
    action: 'typing',
    room_id: currentRoomId,
    typing: true
  }));

  // Clear any existing timer
  if (window.typingTimer) clearTimeout(window.typingTimer);

  // After 2 seconds of no input, send "typing: false"
  window.typingTimer = setTimeout(() => {
    chatSocket.send(JSON.stringify({
      action: 'typing',
      room_id: currentRoomId,
      typing: false
    }));
  }, 2000);

  // Check for '@' to trigger mention suggestions:
  // Find the last occurrence of '@' in the input value.
  const atIndex = inputValue.lastIndexOf('@');
  if (atIndex !== -1) {
    // Extract the text following the '@'
    const query = inputValue.substring(atIndex + 1);
    
    // Only trigger suggestions if there is some query text (e.g., at least 1 character)
    if (query.length > 0) {
      console.log("query.length");
      // Filter roomMembers array to match the query (case-insensitive)
      const suggestions = roomMembers.filter(member => 
        member.username.toLowerCase().startsWith(query.toLowerCase())
      );

      console.log("problem", suggestions);
      // Show suggestions in the UI
      showMentionSuggestions(suggestions, atIndex);
    } else {
      // Optionally hide suggestions if no query text
      hideMentionSuggestions();
    }
  } else {
    // Hide suggestions if '@' is not found
    hideMentionSuggestions();
  }



}


// Example functions to update your UI with suggestions
function showMentionSuggestions(suggestions, atIndex) {
  const suggestionBox = document.getElementById('mentionSuggestions');
  suggestionBox.style.marginBottom = "10px"
  suggestionBox.style.display = "flex"
  const suggestionDiv = document.getElementById('suggestion-div');
  suggestionBox.innerHTML = ''; // Clear previous suggestions
  suggestions.forEach(username => {
    console.log("username",username);
    const item = document.createElement('div');
    item.classList.add('suggestion-item', 'text-red-500', 'cursor-pointer');
    item.textContent = username.username;
    console.log("for", item);
    item.addEventListener('click', () => {
      insertMention(username.username, atIndex);
      hideMentionSuggestions();
    });
    suggestionBox.appendChild(item);
  });
  suggestionDiv.style.display = 'block';
  suggestionBox.style.display = 'flex';
}

function hideMentionSuggestions() {
  console.log("hide");
  const suggestionBox = document.getElementById('mentionSuggestions');
  // const suggestionDiv = document.getElementById('suggestion-div');
  // suggestionDiv.style.display = 'none';

  suggestionBox.style.display = 'none';
}

// insert suggested user
function insertMention(username, atIndex) {
  const inputEl = document.getElementById('message');
  const value = inputEl.value;
  // Replace the text after the '@' with the full username
  const beforeAt = value.substring(0, atIndex);
  // add a trailing space after the mention.
  inputEl.value = `${beforeAt}@${username} `;
  // Optionally, set the caret at the end of the input.
  inputEl.focus();
}


// formatting message to highlight when a user is tagged. using regex to find when a user is tagged
function formatMessage(messageText) {
  const mentionRegex = /@[A-Za-z0-9._-]+(?:@[A-Za-z0-9.-]+\.[A-Za-z]{2,})?/g;
  return messageText.replace(
    mentionRegex,
    `<span class="mention" style="color: purple;">$&</span>`
  );
}




// to updae the chat and move the message div to the top and to update message count
function updateChatList(id, message, timestamp, sender) {  
  if(sender !== userId && dontUpdateMessageNumber === false){
    messageCount++
  }
    let messageId = `chat-room-${id}`; 
    let roomDiv = `roomDivParent-${id}`; 
    let messageNumber = `messageNumber-${id}`; 
    let messageList = document.getElementById("all-individual-groups");
    let individualMessage = document.getElementById(messageId);
    let roomDivParent = document.getElementById(roomDiv);

    console.log("roomDivParent",roomDivParent, id, roomDiv);

    if (individualMessage) {
        // Updating the second child (message content)
        let messageText = individualMessage.querySelector(".text-sm");
        if (messageText) messageText.textContent = message;

        // Update timestamp (if there's an element for it)
        let timestampElement = individualMessage.querySelector(".xs"); // Add a timestamp div in HTML
        if (timestampElement) timestampElement.textContent = timestamp;

        if (messageCount > 0 && dontUpdateMessageNumber === false){
          let numberDiv = document.getElementById(messageNumber)
          let numberDiv2 = document.getElementById("message-number")
          console.log(numberDiv);
          numberDiv.style.opacity = 1
          numberDiv2.style.opacity = 1
          numberDiv.textContent = messageCount
          numberDiv2.textContent = messageCount
          numberDiv2.className = "text-red-500"
        }

        // Move to top without flickering
        messageList.prepend(roomDivParent);
    } else {
        console.error(`Message with ID "${messageId}" not found.`);
    }
}


document.getElementById("message").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    event.preventDefault(); 
    sendMessage(); 
  }
});

  document.getElementById("chat-message-submit").addEventListener('click', function(){
    sendMessage()
  })

  function openOptions(e){
    let messageOptions = e.target.nextElementSibling

    if(messageOptions && messageOptions.style.display === "flex"){
      messageOptions.style.display = "none"
    }else if(messageOptions.style.display === "none"){
      messageOptions.style.display = "flex"
    }
  }

  // Function to get all individual message to the UI
  function addMessage(username,deleted, message, timestamp, id, sender, replymsg, replyMsgId, media) {
    console.log("omo","why");
    let iconString = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-3 text-gray-500 cursor-pointer">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" /> onClick="openOptions()"
                      </svg>`
                      const formattedText = formatMessage(message);
    const chatMessages = document.getElementById('message-body')
    const msgDiv = document.createElement('div');
    const icon = document.createElement('div');
    const messageOptions = document.createElement('div');
    const iconUsernameAndDate = document.createElement('div');
    const usernameAndDate = document.createElement('div');
    const messageBody = document.createElement('div');
    const replyMessage = document.createElement('p');
    const deleteMessage = document.createElement('p');
    const highlightMessage = document.createElement('p');

    const mainMessageContent = document.createElement('div');
    mainMessageContent.setAttribute("id", `message-child-${id}`);
    const replyMsgDiv = document.createElement('div');
    mainMessageContent.textContent = formattedText;
    mainMessageContent.style.textAlign = "start"

    const wrapperDivId = [];

    console.log("oooo", media);

    if(media.length > 0){
      const wrapper = document.createElement("div");
      console.log("clg", media.length);
      if(media.length > 2){
        wrapper.className = "image-message-parent w-fit grid grid-cols-2"
      }else{
        wrapper.className = "image-message-parent w-fit flex gap-[4px]"

      }
      let chatMedia = document.getElementById("chat-media")
      for (const item of media) {
        console.log("item", item);
        
        const mediaElement = document.createElement("div");
        mediaElement.className = "w-fit  cursor-pointer";
        wrapperDivId.push(item.public_id)
        mediaElement.setAttribute("id", item.public_id);
        mediaElement.addEventListener('click', ()=>{
          console.log("mediachat");
          const img = document.createElement("img")
          img.src = item.url;
          img.classList.add("shadow-md","w-full"); 
          chatMedia.innerHTML = ""
          chatMedia.append(img)
        document.getElementById("view-chat-media").style.display= "flex"
        })
        if (item.type === "video") {
          mediaElement.innerHTML = `<video src="${item.url}" width="180" controls></video>`;
        } else if (item.type === "image") {
          mediaElement.innerHTML = `<img src="${item.url}" width="180">`;
        }

        wrapper.append(mediaElement);
      }
      mainMessageContent.append(wrapper)
    }

      

    if(replymsg !== "None" && replyMsgId !== null){
      console.log("replymsg",replymsg);
      replyMsgDiv.innerHTML= `
      <div id= message-child-${id} style="text-align: start;">
        <div class="w-full flex flex-col gap-4 bg-gray-200 text-gray-600 text-transform-none border-l-2 border-green-200 p-4 rounded-t-md mb-1" onClick="findRepliedMessage(${replyMsgId})">
        <p class="text-black">${sender}</p>
        <p>${replymsg}</p>
        </div>
      </div> `
      messageBody.appendChild(replyMsgDiv)
      messageBody.appendChild(mainMessageContent)
    }else{
      if(deleted){
        messageBody.className = "text-red-500 justify-self-start"
      }else{
        messageBody.className = "justify-self-start";
      }
      messageBody.appendChild(mainMessageContent);
    }
      

      //  Setting their ids and event listeners
      replyMessage.setAttribute("data-id", id);
      replyMessage.addEventListener("click", (e) => {
        replyMessageId = e.currentTarget.getAttribute("data-id");
        const messageElement = document.querySelector(`[data-message-id="${id}"]`);
        const replyMessageDiv = document.getElementById("reply-message-div")
        const messageInput = document.getElementById("message")
        messageInput.focus()
        const gottenReplyMessageUsername= e.target.parentElement.parentElement;
        const replyMessageUsername= document.createElement('p');
        replyMessageUsername.className = "text-green-800"
        const replyMessageContent = document.createElement('p');
        if (messageElement) {
          replyMessageContent.textContent = messageElement.textContent;
          replyMessageContent.className = "text-black"
          console.log("Message text:", messageElement.textContent);
        } else {
          replyMessageContent.textContent = "--";
        }
        
        replyMessageUsername.textContent = gottenReplyMessageUsername.previousSibling.children[0].textContent
        replyMessageDiv.style.display = "block"
        replyMessageDiv.children[0].append(replyMessageUsername)
        replyMessageDiv.children[0].append(replyMessageContent)
        document.getElementById("suggestion-div").style.display = "block";

        
        e.target.parentElement.style.display = "none"
      });
      
      deleteMessage.setAttribute("data-delete-id", id);
      deleteMessage.addEventListener("click", (e)=>{
        console.log("lls",id, wrapperDivId);
        let messageChild = document.getElementById(`message-child-${id}`);
        messageChild.innerHTML = ""
        e.target.parentElement.style.display = "none"

      const payload = {
        action: "delete",
        message_id: id,
      };

      // Only include media if publicIds is provided and not empty
      if (wrapperDivId && wrapperDivId.length > 0) {
        payload.public_ids = wrapperDivId;
      }

      chatSocket.send(JSON.stringify(payload));

      })



      messageBody.style.textTransform = "none"; 
      messageBody.style.fontFamily = "'Rubik', sans-serif";
      messageBody.style.fontSize = "13px";
      const msgDivDate = document.createElement('p');
      const msgDivUsername = document.createElement('p');
      replyMessage.innerHTML = "reply";
      deleteMessage.innerHTML = "delete";
      highlightMessage.innerHTML = "highlight";
      messageBody.setAttribute("data-message-id", id)
      icon.innerHTML = iconString;
      msgDivDate.textContent = timestamp;
      msgDivUsername.textContent = username;
      
      messageOptions.className = "message-options flex-col gap-4 bg-white w-fit absolute w-fit p-3 bottom-[-1rem] right-4";
      messageOptions.style.display = "none"
      replyMessage.className = "cursor-pointer text-black hover:bg-gray-100 p-2";
      deleteMessage.className = "cursor-pointer text-black hover:bg-gray-100 p-2";
      highlightMessage.className = "cursor-pointer text-black hover:bg-gray-100 p-2";
      
      msgDiv.className = "p-2 border-b relative";
      msgDivUsername.className = "text-[#417690] text-bold";
      msgDivDate.className = "text-gray-300 text-small";
      
      iconUsernameAndDate.className = "flex justify-between";
      usernameAndDate.className = "flex gap-4";
      messageOptions.appendChild(replyMessage)
      messageOptions.appendChild(deleteMessage)
      messageOptions.appendChild(highlightMessage)
      icon.appendChild(messageOptions)
      icon.addEventListener("click", (e)=>openOptions(e))
      usernameAndDate.appendChild(msgDivUsername)
      usernameAndDate.appendChild(msgDivDate)
      iconUsernameAndDate.prepend(usernameAndDate)
      iconUsernameAndDate.appendChild(icon)
      msgDiv.prepend(iconUsernameAndDate)
      msgDiv.append(messageBody)
      if(prependMode){
        chatMessages.prepend(msgDiv);
      }else{

        chatMessages.append(msgDiv);
        // chatMessages.scrollTop = chatMessages.scrollHeight;
      }
  }


  replyMessageCancel.addEventListener("click", (e)=>{
    document.getElementById("suggestion-div").style.display= "none"
    document.getElementById("reply-message-div").style.display = 'none'
    console.log( "doc",document.getElementById("reply-message-div"));
    const container = e.currentTarget.parentElement;
    console.log("cont", container);
  
    const adminEl = container.querySelector("p.text-green-800");
    const outletEl = container.querySelector("p.text-black");
    adminEl.remove()
    outletEl.remove()
    console.log("adddd", adminEl);
  })


const messageBody = document.getElementById("message-body");

// messageBody.addEventListener("scroll", () => {
//   console.log("eweee");
//   globalMessageheight = true
//   prependMode = true
//   if (messageBody.scrollTop === 0 && !isLoading) {
//     isLoading = true;
//     currentPage += 1;

//     // Save current scroll height before new messages load

//     scrollFromBottom = messageBody.scrollHeight - messageBody.scrollTop;

//     // Request older messages
//     chatSocket.send(JSON.stringify({
//       action: "load_messages",
//       room_id: currentRoomId,
//       page: currentPage
//     }));

//     globalMessageScroll = messageBody.scrollTop

//   }
// });

// Debugging function to log scroll details


messageBody.addEventListener("scroll", (event) => {
  // Check if we're within 10 pixels of the top
  globalMessageheight = true
  const isNearTop = event.target.scrollTop <= 10;

  if (isNearTop && !isLoading) {
      console.log("Near top of messages, loading previous messages");
      
      isLoading = true;
      currentPage += 1;

      // Save current scroll height before new messages load
      // scrollFromBottom = event.target.scrollHeight - event.target.scrollTop;
          scrollFromBottom = messageBody.scrollHeight - messageBody.scrollTop;


      // Request older messages
      chatSocket.send(JSON.stringify({
          action: "load_messages",
          room_id: currentRoomId,
          page: currentPage
      }));


      prependMode = true

      console.log("prepend", prependMode);
      // globalMessageScroll = event.target.scrollTop;
      globalMessageScroll = messageBody.scrollTop
  }
});


  
  // update the ui of the chts
  function updateChatRooms(rooms) {
    const allIndividualGroups = document.getElementById("all-individual-groups");
    if(rooms.action === "room_list"){
      allIndividualGroups.innerHTML = "";
    }
    console.log("object",rooms);

    if (rooms.rooms.length > 0) {
      if(rooms.action === "new_room"){
        console.log("rooms.rooms",rooms.rooms);
        rooms.rooms.forEach(room => {
        console.log(room);
        console.log(room.id);
            const roomDiv = document.createElement("div");
            roomDiv.setAttribute("id", `chat-room-${room.id}`)
            roomDiv.className = "cursor-pointer hover:bg-gray-100 p-3 border-b border-gray-200";
            roomDiv.innerHTML = `
                <div class="font-semibold text-gray-800">${room.name}</div>
                <div class="text-sm text-gray-500 truncate">You have just been added to this room</div>
            `;
            const searchId = 0
            const messages="empty"
            const openChatType = "message";

            roomDiv.addEventListener("click", function () {openChatRoom(room.id, messages,  openChatType, room.name, searchId);});
            user_room_types = "group_chat"
            roomDetails[room.name] =  room.id

            allIndividualGroups.prepend(roomDiv);
        });
      }
      else if(rooms.action === "room_list"){
        rooms.rooms.forEach(room => {
            const roomDiv = document.createElement("div");
            const roomDivParent = document.createElement("div");
            const newMessageNumber = document.createElement("div");
            roomDiv.setAttribute("id", `chat-room-${room.id}`)
            roomDiv.className = "w-[80%]";
            roomDiv.innerHTML = `
                <div class="font-semibold text-gray-800">${room.name}</div>
                <div class="text-sm text-gray-500 truncate">${room.last_message}</div>
                <div class="text-xs text-gray-400">${room.last_message_time}</div>
                <div></div>
            `;
            const searchId = 0
            const messages="empty";
            const openChatType = "message";
            roomDiv.addEventListener("click", function () {openChatRoom(room.id,messages,  openChatType, room.name, searchId);});
            user_room_types = "group_chat"
            roomDetails[room.name] =  room.id

            newMessageNumber.className = 'w-[20px] h-[20px] bg-red-600 text-white opacity-0 rounded-full flex justify-center items-center'
            // newMessageNumber.style.display = "none"
            newMessageNumber.setAttribute('id', `messageNumber-${room.id}`)
            roomDivParent.setAttribute('id', `roomDivParent-${room.id}`)
            roomDivParent.className = 'w-full hover:bg-gray-100 p-3 flex items-center justify-around cursor-pointer border-b border-gray-200'
            // roomDivParent.setAttribute('id', `roomDivParent-${room.id}`)
            roomDivParent.appendChild(newMessageNumber);
            roomDivParent.appendChild(roomDiv);
            allIndividualGroups.appendChild(roomDivParent);
        });
      }
    } else {
      allIndividualGroups.innerHTML = `<div class="text-gray-500 p-3">No chat rooms available.</div>`;
    }
  }


  // Modal open and close logic
  document.getElementById('openModalBtn').addEventListener('click', () => {
    createChatModal.classList.remove('hidden');
  });
  document.getElementById('closeModalBtn').addEventListener('click', () => {
    createChatModal.classList.add('hidden');
  });

  // Live search for users
  function liveSearchUsers() {
    const query = document.getElementById('userSearch').value;
    const resultsDiv = document.getElementById('searchResults');
    const noUserDiv = document.getElementById('noUserFound');
    
    if (query.length < 2 ) {
      resultsDiv.innerHTML = '';
      noUserDiv.classList.add('hidden');
      return;
    }
    
    fetch(`/chat/live_admin_user_search/?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        resultsDiv.innerHTML = '';
        if (data.users && data.users.length > 0) {
          noUserDiv.classList.add('hidden');
          data.users.forEach(user => {
            console.log(user);
            const userDiv = document.createElement('div');
            userDiv.className = 'flex items-center justify-between border-b border-gray-200 py-2 text-[#417690]';
            userDiv.innerHTML = `
              <span>${user.email}</span>
              <button onclick="addUserToRoom('${user.id}', '${user.username}')" class="text-blue-500 hover:text-blue-700">Add</button>
            `;
            resultsDiv.appendChild(userDiv);
          });
        } else {
          resultsDiv.innerHTML = '';
          noUserDiv.classList.remove('hidden');
        }
      })
      .catch(error => {
        console.error('Error searching users:', error);
      });
  }


  // Keep track of selected user IDs
  let addedUserIds = [];
 

  // Add user to selected list
  function addUserToRoom(userId, username) {
  console.log("oghene");
    if (addedUserIds.includes(userId)) return;
    addedUserIds.push(userId);
    
    const selectedUsersDiv = document.getElementById('selectedUsers');
    const userEntry = document.createElement('div');
    userEntry.className = 'flex items-center justify-between p-2 bg-gray-100 rounded mt-2 text-[#417690]';
    userEntry.innerHTML = `
      <span>${username}</span>
      <button onclick="removeUserFromRoom('${userId}', this)" class="text-red-500 hover:text-red-700">Remove</button>
    `;
    selectedUsersDiv.appendChild(userEntry);
    
    // Optionally, clear search results and input
    document.getElementById('searchResults').innerHTML = '';
    document.getElementById('userSearch').value = '';
  }

  

  // Remove a user from selected list
  function removeUserFromRoom(userId, btn) {
    addedUserIds = addedUserIds.filter(id => id !== userId);
    btn.parentElement.remove();
  }

  //#region Create Room (POST Request)
  const createRoomBtn = document.getElementById('createRoomBtn');
  
  createRoomBtn.addEventListener('click', () => {
    const roomName = document.getElementById('roomName').value.trim();
    if (!roomName) {
      alert("Please enter a room name.");
      return;
    }

    // Build the POST data
    const payload = {
      roomName: roomName,
      members: addedUserIds
    };
  // If you're using Django's CSRF protection in templates, grab the token:
  const csrfToken = getCookie('csrftoken'); // defining a getCookie below

  fetch('/chat/chat/create_room/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',  // ensures cookies are sent
    body: JSON.stringify(payload)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      Toastify({
        text: `Room '${data.roomName}' created successfully!`,
        duration: 3000, // Time in milliseconds (3 seconds)
        close: true, // Show close button
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center`, or `right`
        backgroundColor: "linear-gradient(to right, #00b09b, #417690)",
      }).showToast();
      // Clear fields and close modal
      document.getElementById('roomName').value = '';
      addedUserIds = [];
      document.getElementById('selectedUsers').innerHTML = '';
      createChatModal.classList.add('hidden');
      // Optionally redirect to the chat room page
      // window.location.href = `/chat/room/${data.roomName}/`;
    } else {
      Toastify({
          text: `Sorry! an error occured-Error: ${data.error}`,
          duration: 3000, // Time in milliseconds (3 seconds)
          close: true, // Show close button
          gravity: "top", // `top` or `bottom`
          position: "right", // `left`, `center`, or `right`
          backgroundColor: "linear-gradient(to right, #ff4d4d, #ff0000)",
      }).showToast();
      alert();
    }
  })
  .catch(error => {
    console.error('Error creating room:', error);
  });
  });

  

  //#endregion

  

  //#region admin add users
  const adminCloseModalBtn = document.getElementById('admin-closeModalBtn');
  const adminAddUsers = document.getElementById('admin-add-users');


  function adminLiveSearchUsers() {
    const adminQuery = document.getElementById('admin-userSearch').value;
    const adminResultsDiv = document.getElementById('admin-searchResults');
    const adminNoUserDiv = document.getElementById('admin-noUserFound');
    
   
    if (adminQuery.length < 2 ) {
      adminResultsDiv.innerHTML = '';
      adminNoUserDiv.classList.add('hidden');
      return;
    }
    
    fetch(`/chat/live_admin_user_search/?q=${encodeURIComponent(adminQuery)}`)
      .then(response => response.json())
      .then(data => {
        adminResultsDiv.innerHTML = '';
        if (data.users && data.users.length > 0) {
          adminNoUserDiv.classList.add('hidden');
          data.users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.className = 'flex items-center justify-between border-b border-gray-200 py-2 text-[#417690]';
            userDiv.innerHTML = `
              <span>${user.email}</span>
              <button onclick="adminAddUserToRoom('${user.id}', '${user.username}')" class="text-blue-500 hover:text-blue-700">Add</button>
            `;
            adminResultsDiv.appendChild(userDiv);
          });
        } else {
          adminResultsDiv.innerHTML = '';
          adminNoUserDiv.classList.remove('hidden');
        }
      })
      .catch(error => {
        console.error('Error searching users:', error);
      });
  }

  let adminAddedUserIds = [];
  

  function adminAddUserToRoom(userId, username) {
    if (adminAddedUserIds.includes(userId)) return;
    adminAddedUserIds.push(userId);
    
    const selectedUsersDiv = document.getElementById('admin-selectedUsers');
    const userEntry = document.createElement('div');
    userEntry.className = 'flex items-center justify-between p-2 bg-gray-100 rounded mt-2 text-[#417690]';
    userEntry.innerHTML = `
      <span>${username}</span>
      <button onclick="adminRemoveUserFromRoom('${userId}', this)" class="text-red-500 hover:text-red-700">Remove</button>
    `;
    selectedUsersDiv.appendChild(userEntry);
    
    // Optionally, clear search results and input
    document.getElementById('admin-searchResults').innerHTML = '';
    document.getElementById('admin-userSearch').value = '';
  }


  addUserToGroup.addEventListener("click",()=>{
    adminAddUserRoomTitle = document.getElementById("roomTitle").innerHTML;
    addUserModal.style.display= "flex"
  })

  adminAddUsers.addEventListener('click', () => {
    // Build the POST data
    const payload = {
      members: adminAddedUserIds
    };
  // If you're using Django's CSRF protection in templates, grab the token:
  const csrfToken = getCookie('csrftoken'); // defining a getCookie below

  fetch(`/chat/rooms/${roomDetails[adminAddUserRoomTitle]}/add-members/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',  // ensures cookies are sent
    body: JSON.stringify(payload)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      adminAddedUserIds = []
      document.getElementById('admin-selectedUsers').innerHTML = '';
      addUserModal.classList.add('hidden');
      Toastify({
        text: "Users added successfully",
        duration: 3000, // Time in milliseconds (3 seconds)
        close: true, // Show close button
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center`, or `right`
        backgroundColor: "linear-gradient(to right, #00b09b, #417690)",
    }).showToast();
    } else {
      Toastify({
        text: "Sorry! an error occured",
        duration: 3000, // Time in milliseconds (3 seconds)
        close: true, // Show close button
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center`, or `right`
        backgroundColor: "linear-gradient(to right, #ff4d4d, #ff0000)",
    }).showToast();
    }
  })
  .catch(error => {
    console.error('Error adding user to room:', error);
  });
  });


  adminCloseModalBtn.addEventListener("click", ()=>{
    addUserModal.style.display = "none"
  })

  adminleaveRoomButton.addEventListener("click", ()=>{
    adminAddUserRoomTitle = document.getElementById("roomTitle").innerHTML;
    leaveRoomYesOrNoModal.style.display = "flex"
  })

  adminDeleteRoomButton.addEventListener("click", ()=>{
    adminAddUserRoomTitle = document.getElementById("roomTitle").innerHTML;
    deleteRoomYesOrNoModal.style.display = "flex"
  })

  leaveRoomCloseModalBtn.addEventListener("click", ()=>{
    leaveRoomYesOrNoModal.style.display = "none"
  })


  leaveRoomConfirm.addEventListener('click', () => {
    
  // If you're using Django's CSRF protection in templates, grab the token:
  const csrfToken = getCookie('csrftoken'); // defining a getCookie below

  fetch(`/chat/rooms/${roomDetails[adminAddUserRoomTitle]}/leave/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    credentials: 'include',  // ensures cookies are sent
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      leaveRoomYesOrNoModal.classList.add('hidden');
      Toastify({
        text: "Users added successfully",
        duration: 3000, // Time in milliseconds (3 seconds)
        close: true, // Show close button
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center`, or `right`
        backgroundColor: "linear-gradient(to right, #00b09b, #417690)",
    }).showToast();
        
  } else {
      Toastify({
        text: "Sorry! an error occured",
        duration: 3000, // Time in milliseconds (3 seconds)
        close: true, // Show close button
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center`, or `right`
        backgroundColor: "linear-gradient(to right, #ff4d4d, #ff0000)",
    }).showToast();
    }
  })
  .catch(error => {
    console.error('Error adding user to room:', error);
  });
  });

  
  deleteRoomCloseModalBtn.addEventListener("click", ()=>{
    deleteRoomYesOrNoModal.style.display = "none"
  })


  deleteRoomConfirm.addEventListener('click', () => {
      
    // If you're using Django's CSRF protection in templates, grab the token:
    const csrfToken = getCookie('csrftoken'); // defining a getCookie below

    fetch(`/chat/rooms/${roomDetails[adminAddUserRoomTitle]}/delete/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'include',  // ensures cookies are sent
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        deleteRoomYesOrNoModal.classList.add('hidden');
        let roomId = `chat-room-${roomDetails[adminAddUserRoomTitle]}`
        let room = document.getElementById(roomId)
        messageBodyParent.style.display = "none"  
        chatContainer.style.display = "block"  
        console.log(roomId, roomId);
        room.style.display = "none"
        Toastify({
          text: "Room deleted successfully",
          duration: 3000, // Time in milliseconds (3 seconds)
          close: true, // Show close button
          gravity: "top", // `top` or `bottom`
          position: "right", // `left`, `center`, or `right`
          backgroundColor: "linear-gradient(to right, #00b09b, #417690)",
      }).showToast();
      } else {
        Toastify({
          text: "Sorry! an error occured",
          duration: 3000, // Time in milliseconds (3 seconds)
          close: true, // Show close button
          gravity: "top", // `top` or `bottom`
          position: "right", // `left`, `center`, or `right`
          backgroundColor: "linear-gradient(to right, #ff4d4d, #ff0000)",
      }).showToast();
      }
    })
    .catch(error => {
      console.error('Error adding user to room:', error);
    });
  });

  
  //#endregion


  

  // Helper function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }


// peronal chat region
let personalMessagePage = document.getElementById("personal-message-page")
let mainMenu = document.getElementById('main-menu')
let onlineStatusBar = document.getElementById('online-bar-status')
let onlineTab = document.getElementById('online-tab')
let chatTab = document.getElementById('chat-tab')
let menuparent = document.getElementById('menuparent')
let chatOnlineBackArrow = document.getElementById('chat-online-back-arrow')
const onlineStatusContainer = document.getElementById('onlineStatusList');
const broadcastToAllAgents = document.getElementById('broadcast-all-agent');
const broadcastToAllHO = document.getElementById('broadcast-all-ho');



// chatOnlineBackArrow
chatOnlineBackArrow.addEventListener("click", ()=>{
  menuparent.style.display = "block"
  if(onlineStatusContainer.style.display = "block"){
    onlineStatusContainer.style.display = "none"

  }
  chatOnlineBackArrow.style.display = "none"
  onlineTab.style.textDecoration = "none"
  chatTab.style.textDecoration = "underline"

})

// open onlone chat
onlineTab.addEventListener("click", ()=>{
  console.log("mannny");
  chatOnlineBackArrow.style.display = "block"
  onlineTab.style.textDecoration = "underline"
  chatTab.style.textDecoration = "none"
  menuparent.style.display = "none"
  onlineStatusContainer.style.cssText = "display:flex; flex-direction:column;"
})

chatTab.addEventListener("click", ()=>{
  chatTab.style.textDecoration = "underline"
  onlineTab.style.textDecoration = "none"
  menuparent.style.display = "block"
  onlineStatusContainer.style.display = "none"

})

// open personal chat
broadcastToAllAgents.addEventListener("click", ()=>{
  personalMessagePage.style.display = "block"
  personalMessageBodyParent.style.display = "none"
})
broadcastToAllHO.addEventListener("click", ()=>{
  personalMessagePage.style.display = "block"
  personalMessageBodyParent.style.display = "none"
})
document.getElementById("personal-chat").addEventListener("click", ()=>{
  console.log("personal-message-page");
  menuparent.style.display = "none"
  personalMessagePage.style.display = "block"
  personalMessageBodyParent.style.display = "block"
})

// go back to menu page

if(personalMessageBackArrow){
  personalMessageBackArrow.addEventListener("click", ()=>{
    onlineStatusContainer.style.display = "none"
    personalMessagePage.style.display = "none"
    menuparent.style.display = "block"
    mainBody.style.display = "block"
  })

}

       
// function to show online or offline
function renderOnlineStatus(user, online_status, username, status_id, room_name) {
  // if(userId === username){
  //   let noUser = document.createElement("p")
  //   noUser.setAttribute("id", "noUser")
  //   container
  //   return
  // }

  // if(userId === username){return}
  console.log(username,"poppoo", userId);
    if(online_status === "offline"){
      let onlineStatusChild = document.getElementById(user)
      console.log("status", onlineStatusChild, user);
      if(onlineStatusChild){
        onlineStatusChild.remove()
      }
      return
    }
    const statusItem = document.createElement('div');
    statusItem.classList.add('online-status-item');
    statusItem.setAttribute("id", user);
    statusItem.setAttribute("data-online-id", status_id);
    roomDetails[room_name] = status_id
    console.log("later", roomDetails);
    
    let type = "private"
    let messages = null
    let searchId = null
    statusItem.addEventListener("click", (e)=>{
      console.log("dey", e);
      menuparent.style.display = "none"
      personalMessagePage.style.display = "block"
      personalMessageBodyParent.style.display = "block"
      openChatRoom(status_id, messages, type, room_name,searchId)
    })
    user_room_types = "private"

    const emailSpan = document.createElement('span');
    emailSpan.textContent = user;

    const statusIndicator = document.createElement('div');
    statusIndicator.classList.add('status-indicator');

    statusItem.appendChild(emailSpan);
    statusItem.appendChild(statusIndicator);
    onlineStatusContainer.prepend(statusItem);
}


grouindividualGroupParentsChat.addEventListener("scroll", (event) => {
  // Check if we're within 10 pixels of the top
  globalMessageheight = true
  const isNearTop = event.target.scrollTop <= 10;

  if (isNearTop && !isLoading) {
      console.log("Near top of messages, loading previous messages");
      
      isLoading = true;
      currentPage += 1;

      // Save current scroll height before new messages load
      // scrollFromBottom = event.target.scrollHeight - event.target.scrollTop;
          scrollFromBottom = messageBody.scrollHeight - messageBody.scrollTop;


      // Request older messages
      chatSocket.send(JSON.stringify({
          action: "load_messages",
          room_id: currentRoomId,
          page: currentPage
      }));


      prependMode = true

      console.log("prepend", prependMode);
      // globalMessageScroll = event.target.scrollTop;
      globalMessageScroll = messageBody.scrollTop
  }
});
  


function toggleBookingView(){
  if (teamMember.style.display != 'none'){
      teamMember.style.display = 'none'
      rolesPermission.style.display = 'block'

     
  }
  else if(rolesPermission.style.display != 'none'){
      teamMember.style.display = 'block'
      rolesPermission.style.display = 'none'

     
  }
}


