```json
<HTTP 엔드포인트>

/register - 뭐긴 뭐야 회원가입 하는 곳이지(POST)
/login - 로그인 하는 API (POST인데 나중에 GET으로 바꿀꺼, OK: 201와 Token, FAIL: 401)
        
<웹소켓>

타입:
handshake: 핸드쉐이크시 데이터 교환에 사용
error: 뭐긴 뭐야 에러지 시발
{
	"code": "코드",
	"reason": "이유"
}

heartbeat: 하트비트 ㅇㅇ 페이로드에 있는 값은 돌려줌
ㄴ heartbeat timeout이면 Websocket Closed 시키는 거 좀 만들자 

chat: 채팅
{
	"type": "send, edit 중 하나",
	"user_id": "유저아이디, 서버에서 보낼때만 들어감",
	"chat_id": "채팅방 아이디",
	"content": "대충 내용, send에서 비어있을 시 무시, edit에서 비어있을 시 삭제"
}

user: 사용자
{
	"id": "아이디",
	"name": "이름",
	"profile": "(대충 프로필 주소 넣어주기)"
}

기본 데이터 틀:
{
	"type": "",
	"payload": ""
}
        
유저 정보:
-===악수===-
Client:
type handshake
payload {
	"auth": "대충 토큰을 쳐 박으새오"
}
        
Server:
type handshake
payload {
	"user_info": "user오브젝트를 쳐 박으새오!",
	"friends": ["대충 친구 목록이라는 챗"]
}

<내부 DB>
-추가 요망-
```