import android.net.Uri
import android.os.Bundle
import android.util.DisplayMetrics
import android.view.*
import android.widget.Button
import androidx.fragment.app.DialogFragment
import com.example.kotlin_00.databinding.FragmentVideoPlayerBinding

class VideoPlayerFragment : DialogFragment() {

    private var _binding: FragmentVideoPlayerBinding? = null
    private val binding get() = _binding!!
    private var isPlaying = false

    companion object {
        private const val VIDEO_URL = "video_url"

        fun newInstance(videoUrl: String): VideoPlayerFragment {
            val fragment = VideoPlayerFragment()
            val args = Bundle()
            args.putString(VIDEO_URL, videoUrl)
            fragment.arguments = args
            return fragment
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentVideoPlayerBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val videoUrl = arguments?.getString(VIDEO_URL) ?: return
        binding.videoView.setVideoURI(Uri.parse(videoUrl))

        // **Tam ekran oran ayarı**
        binding.videoView.setOnPreparedListener { mediaPlayer ->
            val videoWidth = mediaPlayer.videoWidth
            val videoHeight = mediaPlayer.videoHeight

            val displayMetrics = DisplayMetrics()
            requireActivity().windowManager.defaultDisplay.getMetrics(displayMetrics)
            val screenWidth = displayMetrics.widthPixels

            val layoutParams = binding.videoView.layoutParams
            layoutParams.width = screenWidth
            layoutParams.height = (screenWidth * videoHeight / videoWidth)
            binding.videoView.layoutParams = layoutParams

            mediaPlayer.start()
            isPlaying = true
        }

        binding.videoView.setOnCompletionListener { dismiss() }

        // **Kontroller**
        binding.btnPlayPause.setOnClickListener {
            if (isPlaying) {
                binding.videoView.pause()
                binding.btnPlayPause.text = "▶️"
            } else {
                binding.videoView.start()
                binding.btnPlayPause.text = "⏸"
            }
            isPlaying = !isPlaying
        }

        binding.btnForward.setOnClickListener {
            binding.videoView.seekTo(binding.videoView.currentPosition + 5000) // 5 saniye ileri
        }

        binding.btnRewind.setOnClickListener {
            binding.videoView.seekTo(binding.videoView.currentPosition - 5000) // 5 saniye geri
        }
    }

    override fun onStart() {
        super.onStart()
        dialog?.window?.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        dialog?.window?.setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        ) // **Tam ekran**
        dialog?.window?.setBackgroundDrawableResource(android.R.color.transparent) // **Şeffaf arka plan**
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
