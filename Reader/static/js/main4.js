// variables
let userName = null;
let state = 'SUCCESS';

// functions
function Message(arg) {
    this.text = arg.text;
    this.message_side = arg.message_side;

    this.draw = function (_this) {
        return function () {
            let $message;
            $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side).find('.text').html(_this.text);
            $('.messages').append($message);

            return setTimeout(function () {
                return $message.addClass('appeared');
            }, 0);
        };
    }(this);
    return this;
}

function getMessageText() {
    let $message_input;
    $message_input = $('.message_input');
    return $message_input.val();
}

function sendMessage(text, message_side) {
    let $messages, message;
    $('.message_input').val('');
    $messages = $('.messages');
    message = new Message({
        text: text,
        message_side: message_side
    });
    message.draw();
    $messages.animate({scrollTop: $messages.prop('scrollHeight')}, 300);
}

function greet() {
    setTimeout(function () {
        return sendMessage("Kochat 데모에 오신걸 환영합니다.", 'left');
    }, 1000);

    setTimeout(function () {
        return sendMessage("사용할 닉네임을 알려주세요.", 'left');
    }, 2000);
}

function onClickAsEnter(e) {
    if (e.keyCode === 13) {
        onSendButtonClicked()
    }
}

function setUserName(username) {

    if (username != null && username.replace(" ", "" !== "")) {
        setTimeout(function () {
            return sendMessage("반갑습니다." + username + "님. 닉네임이 설정되었습니다.", 'left');
        }, 1000);
        setTimeout(function () {
            return sendMessage("저는 Reader 서비스의 챗봇 서비스 베타 버전, '리아'입니다.", 'left');
        }, 2000);
        setTimeout(function () {
            return sendMessage("리아는 다음과 같은 기능을 제공합니다.<br><br>1. yes24에서 선정된 베스트셀러 정보를 알려줍니다.<br>2. 지역에 따른 날씨, 미세먼지, 맛집, 관광지 정보를 알려줍니다.", 'left');
        }, 3000);
        setTimeout(function () {
            return sendMessage("앞으로 리아는 더욱 많은 대화 데이터를 수집하여, 훨씬 다양한 기능들을 제공할 예정입니다.🙂", 'left');
        }, 4000);
        setTimeout(function () {
            return sendMessage("베스트셀러를 참고해서 오늘 읽을 책을 골라보세요! 또한, 날씨, 맛집, 관광지 정보를 토대로 여러 유저들과 친분을 쌓아보세요.", 'left');
        }, 5000);

        return username;

    } else {
        setTimeout(function () {
            return sendMessage("올바른 닉네임을 이용해주세요.", 'left');
        }, 1000);

        return null;
    }
}

function requestChat(messageText, url_pattern) {
    $.ajax({
        url: "https://kochat2.run.goorm.io/fit/" + url_pattern + '/' + userName + '/' + messageText,
        type: "GET",
        dataType: "json",
        success: function (data) {
            state = data['state'];

            if (state === 'SUCCESS') {
                return sendMessage(data['answer'], 'left');
            } else if (state === 'REQUIRE_LOCATION') {
                return sendMessage('어느 지역을 알려드릴까요?', 'left');
            } else if (state === 'REQUIRE_DATE') {
                return sendMessage('어느 날 베스트셀러를 알려드릴까요?', 'left');
            }
            else {
                return sendMessage('죄송합니다. 무슨말인지 잘 모르겠어요.', 'left');
            }
        },

        error: function (request, status, error) {
            console.log(error);

            return sendMessage('죄송합니다. 서버 연결에 실패했습니다.', 'left');
        }
    });
}

function onSendButtonClicked() {
    let messageText = getMessageText();
    sendMessage(messageText, 'right');

    if (userName == null) {
        userName = setUserName(messageText);

    } else {
        if (messageText.includes('안녕')) {
            setTimeout(function () {
                return sendMessage("안녕하세요. 저는 Kochat 여행봇입니다.", 'left');
            }, 1000);
        } else if (messageText.includes('고마워')) {
            setTimeout(function () {
                return sendMessage("천만에요. 더 물어보실 건 없나요?", 'left');
            }, 1000);
        } else if (messageText.includes('없어')) {
            setTimeout(function () {
                return sendMessage("그렇군요. 알겠습니다!", 'left');
            }, 1000);


        } else if (state.includes('REQUIRE')) {
            return requestChat(messageText, 'fill_slot');
        } else {
            setTimeout(function () {
                return sendMessage("정보를 수집중입니다...", 'left');
            }, 1000);
            return requestChat(messageText, 'request_chat');
        }
    }
}

