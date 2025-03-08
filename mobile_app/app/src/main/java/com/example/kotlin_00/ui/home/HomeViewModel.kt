package com.example.kotlin_00.ui.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class HomeViewModel : ViewModel() {
    private val _selectedModel = MutableLiveData<String>()
    val selectedModel: LiveData<String> = _selectedModel

    fun setSelectedModel(model: String) {
        _selectedModel.value = model
    }
}

