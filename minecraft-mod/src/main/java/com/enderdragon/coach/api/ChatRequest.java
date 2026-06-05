package com.enderdragon.coach.api;

import com.google.gson.annotations.SerializedName;

import java.util.Collections;
import java.util.List;

/**
 * 백엔드 {@code POST /api/v1/chat/sync} 요청 바디.
 * 백엔드 스키마(app/schemas.py: ChatRequest)와 필드를 맞춘다.
 */
public class ChatRequest {

    public final String message;

    @SerializedName("thread_id")
    public final String threadId;

    public final List<InventorySnapshot.InventoryItem> inventory;

    public ChatRequest(String message, String threadId, List<InventorySnapshot.InventoryItem> inventory) {
        this.message = message;
        this.threadId = threadId;
        this.inventory = inventory != null ? inventory : Collections.emptyList();
    }
}
