package com.example.kotlin_00.ui.videos

import android.net.Uri
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.kotlin_00.databinding.ItemVideoBinding

class VideoAdapter(private val onVideoClick: (String) -> Unit) :
    ListAdapter<String, VideoAdapter.VideoViewHolder>(VideoDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VideoViewHolder {
        val binding = ItemVideoBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return VideoViewHolder(binding)
    }

    override fun onBindViewHolder(holder: VideoViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class VideoViewHolder(private val binding: ItemVideoBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(videoName: String) {
            binding.textViewVideoName.text = videoName
            val encodedVideoName = Uri.encode(videoName)  // .mp4 uzantısı API'de zaten işleniyor
            val thumbnailUrl = "http://192.168.1.103:8000/thumbnails/$encodedVideoName"

            Glide.with(binding.imageViewThumbnail.context)
                .load(thumbnailUrl)
                .placeholder(android.R.drawable.ic_media_play)  // Yüklenirken gösterilecek simge
                .into(binding.imageViewThumbnail)

            binding.root.setOnClickListener {
                onVideoClick(videoName)
            }
        }
    }

    class VideoDiffCallback : DiffUtil.ItemCallback<String>() {
        override fun areItemsTheSame(oldItem: String, newItem: String) = oldItem == newItem
        override fun areContentsTheSame(oldItem: String, newItem: String) = oldItem == newItem
    }
}
