```json
HTTP 엔드포인트

-===인증===-
/token - 토큰을 쳐 받음, Basic으로 인증하던지 알아서 해봐

웹소켓

타입:
handshake: 핸드쉐이크시 데이터 교환에 사용
error: 뭐긴 뭐야 에러지 시발
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
```