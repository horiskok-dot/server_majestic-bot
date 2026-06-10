package com.example.pccontrolmobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.pccontrolmobile.app.PcControlMobileApp
import com.example.pccontrolmobile.core.designsystem.theme.PcControlMobileTheme
import com.example.pccontrolmobile.navigation.PcControlNavHost

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val container = (application as PcControlMobileApp).container
        setContent {
            PcControlMobileTheme {
                PcControlNavHost(container = container)
            }
        }
    }
}
