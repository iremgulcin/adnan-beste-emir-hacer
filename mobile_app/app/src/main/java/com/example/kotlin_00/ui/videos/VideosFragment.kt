package com.example.kotlin_00.ui.videos


import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.kotlin_00.databinding.FragmentVideosBinding
import com.example.kotlin_00.ui.videos.VideoAdapter


class VideosFragment : Fragment() {

    private var _binding: FragmentVideosBinding? = null
    private val binding get() = _binding!!
    private val viewModel: VideosViewModel by viewModels()
    private lateinit var videoAdapter: VideoAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentVideosBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupRecyclerView()

        viewModel.videos.observe(viewLifecycleOwner) { videos ->
            videoAdapter.submitList(videos)
        }

        viewModel.errorMessage.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(context, "Hata: $it", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.fetchVideos()
    }

    private fun setupRecyclerView() {
        videoAdapter = VideoAdapter { videoName ->
            val videoUrl = "http://192.168.1.103:8000/videos/$videoName"
            VideoPlayerFragment.newInstance(videoUrl)
                .show(parentFragmentManager, "VideoPlayerFragment")
        }
        binding.recyclerViewVideos.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = videoAdapter
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
