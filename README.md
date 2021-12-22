# WIND
### DJango -> FLASK & Autobahn 프로젝트<br>

API: https://rewind.icmp.kr<br>
WebSocket: wss://rewind.icmp.kr/ws<br>

#### 구현이 완료된 것들:

```json
<HTTP 엔드포인트>

/register - 회원가입 폼 보낼 수 있는 곳 (테스트 용)

/login - 로그인 폼 보낼 수 있는 곳 (테스트 용)

/api/v1/auth/register - 회원가입 하는 곳 (POST: name, email, password)
{
    "type": "info",
    "payload": {
    	"message": "account successfully created."
    }
}

/api/v1/auth/email_verify/<key> - 이메일 인증 하는 곳 (GET)

/api/v1/auth/login - 로그인 하는 곳 (POST: email, password)
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
heartbeat: 하트비트 ㅇㅇ 페이로드에 있는 값은 돌려 줌 (WS연결이 끊어질 때 까지 반복적으로 확인함, 40 + 5초 내에 하트비트 값 받기 실패시 WS 연결 드랍.)
auth: 인증 (heartbeat를 먼저 받지 않았다면 WS 연결 드랍.)
user: 유저 object
chat: 채팅 object
load: 채팅 기록, 친구 목록 로드 등에 사용됨
mutual_users: 친구 요청 보내기 / 수락 / 삭제, 친구 삭제 기능 
error: 뭐긴 뭐야 에러지 시발

"type": "heartbeat",
"payload": {
   아무 값이나 넣어주셈. 보통은 heartbeat count 넣음.
} (Request & Response(페이로드 값 되돌려 줌))

"type": "auth",
"payload": {
	 "auth": "대충 토큰 보내주기"
} (Request)

"type": "auth",
"payload": {
	 "self_user": "내 정보 보내주기",
	 "mutual_requests": [user objects list] (친추 요청한 user object)
   "mutual_users": [user objects list] (친추된 user object)
} (Response)

"type": "user",
"payload": {
	 "id": "snowflake id",
	 "name": "이름",
	 "profile": "(대충 프로필 주소 넣어주기)" or None
}

"type": "chat",
"payload": {
	 "type": "send, edit 중 하나",
	 "chat_id": "채팅방 아이디(Guild -> 그냥 snowflake id, DM -> user들의 id를 XOR한 값)",
	 "content": "대충 내용, send에서 비어있을 시 무시, edit에서 비어있을 시 삭제, edit에서 내용 있으면 수정"
} (Request)

"type": "chat",
"payload": {
  "type": "send, edit 중 하나",
  "id": "채팅 객체 ID",
  "user_id": "유저 아이디",
  "chat_id": "채팅방 아이디",
  "content": "대충 메시지",
  "created_at": "2021-12-23 00:19:16.000880"
} (Response)

"type": "load",
"payload": {
  "type" : "chat",
  "load_id": "XOR 방이름",
  "datetime": "%Y-%m-%d %H:%M:%S.%f(chat의 created_at 포맷)",
  "count": 갯수(int)
} (Request)

(Response): type이 chat이면 요청한 datetime 기준 전의 채팅 object를 count 수 만큼 반복 전송 함.

"type": "mutual_users",
"payload": {
  "type": "request(친구 추가 요청), response(친구 추가 수락), remove(친구 추가 요청 삭제), delete(친구 삭제(누가 삭제하든 서로 삭제됨))",
  "id": "상대방 snowflake user id"
} (Request)

"type": "mutual_users",
"payload": {
  "type": "위에 거랑 같음",
  "user": "보낸 user의 object"
} (리퀘스트의 대상 클라이언트 Response)

"type": "error",
"payload": {
	"code": "코드",
	"reason": "이유"
} (Response)

<내부 DB>
main:
    snowflake_counter: snowflake를 좀 더 randomize 하기 위한 counter
    user: 유저 정보 들어가있음
    dm_list: dm방 리스트
		
chat:
    dm_{xor-id}: dm 데이터 저장되어있음

friends를 불러올 때 DB 사용: 구현 완료
채팅을 DB에 저장 및 수정, 삭제: 구현 완료
채팅을 DB에서 로드: 구현 완료
DB에서 유저 테이블 로드하여 친구 요청, 추가, 제거: 구현 완료
```


