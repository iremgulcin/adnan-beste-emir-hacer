package com.example.kotlin_00.ui.videos

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import kotlinx.coroutines.launch

class VideosViewModel : ViewModel() {

    private val _videos = MutableLiveData<List<String>>()
    val videos: LiveData<List<String>> = _videos

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    fun fetchVideos() {
        viewModelScope.launch {
            try {
                val videoList = RetrofitClient.instance.getVideos()
                _videos.value = videoList
            } catch (e: Exception) {
                _errorMessage.value = e.message
            }
        }
    }
}
