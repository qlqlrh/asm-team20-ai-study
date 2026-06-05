package com.enderdragon.coach;

import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 클라이언트 진입점.
 *
 * <p>이 모드는 마인크래프트 인게임에서 백엔드 코칭 에이전트(FastAPI)를 호출하는
 * "연결(플러그인화) 기반"이다. 실제 코칭 로직은 백엔드에 있고, 모드는 입력을 받아
 * API를 호출하고 응답을 채팅창에 출력하는 얇은 클라이언트 역할만 한다.
 *
 * <p>이후 단계(4·5번)에서 이 진입점 위에 기능을 확장한다.
 */
public class CoachClientMod implements ClientModInitializer {

    public static final String MOD_ID = "minecraft_coach";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitializeClient() {
        CoachCommand.register();
        LOGGER.info("[{}] 클라이언트 초기화 완료 — '/coach <메시지>'로 코치를 호출하세요.", MOD_ID);
    }
}
