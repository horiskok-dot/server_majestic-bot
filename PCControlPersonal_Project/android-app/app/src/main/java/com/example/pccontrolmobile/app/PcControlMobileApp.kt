package com.example.pccontrolmobile.app

import android.app.Application

class PcControlMobileApp : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}

