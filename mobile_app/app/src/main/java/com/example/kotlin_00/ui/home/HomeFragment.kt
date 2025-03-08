package com.example.kotlin_00.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.example.kotlin_00.databinding.FragmentHomeBinding
import com.example.kotlin_00.BottomSheetFragment
import com.example.kotlin_00.ui.WebSocketClient
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import java.net.URI
import org.json.JSONObject
import android.util.Log

class HomeFragment : Fragment() {

    private lateinit var binding: FragmentHomeBinding
    private lateinit var viewModel: HomeViewModel
    private var player: ExoPlayer? = null
    private var selectedModel: String = "Detection"
    private var socket: WebSocketClient? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        binding = FragmentHomeBinding.inflate(inflater, container, false)
        viewModel = ViewModelProvider(requireActivity())[HomeViewModel::class.java]
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnSelectModel.setOnClickListener {
            BottomSheetFragment().show(parentFragmentManager, "BottomSheetFragment")
        }

        viewModel.selectedModel.observe(viewLifecycleOwner) { model ->
            selectedModel = model
            Toast.makeText(context, "$model seçildi", Toast.LENGTH_SHORT).show()
        }

        binding.btnStartProcessing.setOnClickListener {
            val url = binding.etYouTubeUrl.text.toString().trim()
            if (url.isNotEmpty()) {
                startWebSocket(url)
            } else {
                Toast.makeText(context, "Lütfen geçerli bir URL girin", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun startWebSocket(videoUrl: String) {
        val endpoint = when (selectedModel) {
            "Detection" -> "/detection_ws"
            "Byte Track" -> "/byte_track_ws"
            else -> "/byte_track_ws"
        }
        val wsUrl = "ws://192.168.1.103:8000$endpoint"

        Log.d("WebSocket", "Bağlantı Başlatılıyor: $wsUrl")

        socket = WebSocketClient(URI(wsUrl))

        socket?.onMessageReceived = { message ->
            requireActivity().runOnUiThread {
                try {
                    Log.d("WebSocket", "Gelen Mesaj: $message")
                    val jsonResponse = JSONObject(message)
                    if (jsonResponse.has("video_path")) {
                        val videoPath = jsonResponse.getString("video_path")
                        val fullVideoUrl = "http://192.168.1.103:8000/$videoPath"

                        Log.d("ExoPlayer", "Video Başlatılıyor: $fullVideoUrl")

                        player?.setMediaItem(MediaItem.fromUri(fullVideoUrl))
                        player?.prepare()
                        player?.playWhenReady = true
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    Log.e("WebSocket", "Hata: ${e.message}")
                }
            }
        }

        socket?.connectWithPayload(mapOf("video_url" to videoUrl))
    }

    override fun onDestroyView() {
        super.onDestroyView()
        player?.release()
        socket?.close()
    }
}
