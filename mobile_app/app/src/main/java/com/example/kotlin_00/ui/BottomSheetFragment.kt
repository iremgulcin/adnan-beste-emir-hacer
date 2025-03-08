package com.example.kotlin_00

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.lifecycle.ViewModelProvider
import com.example.kotlin_00.databinding.BottomSheetLayoutBinding
import com.example.kotlin_00.ui.home.HomeViewModel
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment

class BottomSheetFragment : BottomSheetDialogFragment() {

    private lateinit var viewModel: HomeViewModel

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.bottom_sheet_layout, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(requireActivity())[HomeViewModel::class.java]

        view.findViewById<Button>(R.id.btnDetection).setOnClickListener {
            viewModel.setSelectedModel("Detection")
            dismiss()
        }

        view.findViewById<Button>(R.id.btnByteTrack).setOnClickListener {
            viewModel.setSelectedModel("Byte Track")
            dismiss()
        }
    }

    override fun onStart() {
        super.onStart()

        // BottomSheet'in arka planını şeffaf yap
        val dialog = dialog as BottomSheetDialog?
        dialog?.window?.setBackgroundDrawableResource(android.R.color.transparent)

        // Arka planın opaklık seviyesini ayarla (gölgeleme miktarını)
        dialog?.window?.setDimAmount(0.0f) // 0.0f - 1.0f arası değer
    }
}
