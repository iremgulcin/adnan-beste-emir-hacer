package com.example.kotlin_00.ui.videos

import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path

interface VideoApiService {
    @GET("/videos")
    suspend fun getVideos(): List<String>

    @GET("/thumbnails/{videoName}")
    suspend fun getThumbnail(@Path("videoName") videoName: String): Response<ResponseBody>
}

