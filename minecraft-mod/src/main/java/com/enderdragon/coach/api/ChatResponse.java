package com.enderdragon.coach.api;

import java.util.List;

/**
 * 백엔드 {@code POST /api/v1/chat/sync} 응답 바디.
 * 백엔드 스키마(app/schemas.py: ChatResponse)와 필드를 맞춘다.
 */
public class ChatResponse {

    public String answer;
    public String domain;
    public List<String> sources;
    public String disclaimer;

    /** 코치 답변 본문. null 방지용 헬퍼. */
    public String answerOrEmpty() {
        return answer == null ? "" : answer;
    }
}
