# WIND
### DJango -> FLASK  & Autobahn 프로젝트<br>

#### 구현이 완료된 것들:

```json
<HTTP 엔드포인트>

/register - 뭐긴 뭐야 회원가입 하는 곳이지(POST)
/login - 로그인 하는 API (POST)


<웹소켓>

기본 데이터 틀:
{
	"type": "",
	"payload": ""
}

타입:
heartbeat: 하트비트 ㅇㅇ 페이로드에 있는 값은 돌려줌
ㄴ heartbeat timeout이면 Websocket Closed 시키는 거 좀 만들자

handshake: 핸드쉐이크시 데이터 교환에 사용
user: 유저 정보
chat: 뭐긴 뭐야 채팅이지
error: 뭐긴 뭐야 에러지 시발

"type": "handshake",
"payload": {
	"auth": "대충 토큰 보내주기"
} (Client)


"type": "handshake",
"payload": {
	"user_info": "내 정보 보내주기",
	"friends": ["DB에서 친구 목록 가져옴"]
} (Server)

"type": "user",
"payload": {
	"id": "snowflake id",
	"name": "이름",
	"profile": "(대충 프로필 주소 넣어주기)"
}

"type": "chat",
"payload": {
	"type": "send, edit 중 하나",
    "id": "chat object id, edit할 때 id로 select함",
	"user_id": "유저아이디, 클라는 이거 주지 마라",
	"chat_id": "채팅방 아이디(Guild -> 그냥 snowflake id, DM -> user들의 id를 XOR한 값)",
	"content": "대충 내용, send에서 비어있을 시 무시, edit에서 비어있을 시 삭제, edit에서 내용 있으면 수정"
}

"type": "error",
{
	"code": "코드",
	"reason": "이유"
}

<내부 DB>
/register(POST) -> DB
DB -> /login(POST)

friends를 불러올 때 DB 사용: 구현 완료
채팅을 DB에 저장 및 수정, 삭제: 구현 완료
채팅을 DB에서 로드: 구현 중
```
