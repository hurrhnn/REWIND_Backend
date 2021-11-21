# WIND
### DJango -> FLASK  & Autobahn 프로젝트<br>

#### 구현이 완료된 것들:

```json
<HTTP 엔드포인트>

/register - 뭐긴 뭐야 회원가입 하는 곳이지 (POST: name, email, password)
{
    "type": "info",
    "payload": {
    	"message": "account successfully created."
    }
}

/login - 로그인 하는 곳 (POST: email, password)
{
    "type": "auth",
    "payload": {
        "token": "코런건 없어용~"
    }
}


<웹소켓>

기본 데이터 틀:
{
	"type": "",
	"payload": ""
}

타입:
heartbeat: 하트비트 ㅇㅇ 페이로드에 있는 값은 돌려줌(heartbeat timeout이면 Websocket 연결 컷 ㅅㄱ)
auth: 인증을 해야 뭘 하든가 말든가 하지 ㅋㅋ
user: 유저 정보
chat: 채팅임
load: 채팅 기록, 친구 목록 로드 등에 사용될 듯 
error: 뭐긴 뭐야 에러지 시발

"type": "auth",
"payload": {
	"auth": "대충 토큰 보내주기"
} (Client)


"type": "auth",
"payload": {
	"self_user": "내 정보 보내주기",
	"friends": ["DB에서 친구 목록 가져옴"] - onLoad 구현하면 컷 할거임
} (Server)

"type": "user",
"payload": {
	"id": "snowflake id",
	"name": "이름",
	"profile": "(대충 프로필 주소 넣어주기)" or None
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
main:
  impl:
    snowflake_counter: snowflake를 좀 더 randomize 하기 위한 counter
    user: 유저 정보 들어가있음
    dm_list: dm방 리스트
  
  yet:
	room(guild): 단체 채팅 방
	room_list: guild방 리스트 
    ban(?): ban, 사라질 수도 있음
		
chat:
  impl:
    dm_{id}: dm 데이터 저장되어있음
  
  yet:
    room_{id}: Before=room_list

friends를 불러올 때 DB 사용: 구현 완료
채팅을 DB에 저장 및 수정, 삭제: 구현 완료
채팅을 DB에서 로드: 구현 중
```

