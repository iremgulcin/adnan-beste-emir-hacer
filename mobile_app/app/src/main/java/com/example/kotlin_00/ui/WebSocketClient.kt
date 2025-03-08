package com.example.kotlin_00.ui

import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI
import com.google.gson.Gson
import android.util.Log

class WebSocketClient(serverUri: URI) : WebSocketClient(serverUri) {

    var onMessageReceived: ((String) -> Unit)? = null

    override fun onOpen(handshakedata: ServerHandshake?) {
        Log.d("WebSocket", "Bağlantı Açıldı: $uri")
    }

    override fun onMessage(message: String?) {
        message?.let {
            Log.d("WebSocket", "Gelen Mesaj: $it")
            onMessageReceived?.invoke(it)
        }
    }

    override fun onClose(code: Int, reason: String?, remote: Boolean) {
        Log.d("WebSocket", "Bağlantı Kapandı: Kod=$code, Sebep=$reason")
    }

    override fun onError(ex: Exception?) {
        ex?.printStackTrace()
        Log.e("WebSocket", "Hata: ${ex?.message}")
    }

    fun connectWithPayload(payload: Map<String, Any>) {
        try {
            connectBlocking()
            send(Gson().toJson(payload))
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
