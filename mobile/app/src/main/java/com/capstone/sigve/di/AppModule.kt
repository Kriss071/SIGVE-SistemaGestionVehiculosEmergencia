package com.capstone.sigve.di

import android.content.Context
import com.capstone.sigve.BuildConfig
import com.capstone.sigve.data.repository.AuthRepositoryImpl
import com.capstone.sigve.data.repository.SettingsRepository
import com.capstone.sigve.data.repository.VehiclesRepositoryImpl
import com.capstone.sigve.domain.repository.AuthRepository
import com.capstone.sigve.domain.repository.VehiclesRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.auth.Auth
import io.github.jan.supabase.createSupabaseClient
import io.github.jan.supabase.postgrest.Postgrest
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    // Cliente Supabase
    @Provides
    @Singleton
    fun provideSupabaseClient(): SupabaseClient {
        return createSupabaseClient(
            supabaseUrl = BuildConfig.SUPABASE_URL,
            supabaseKey = BuildConfig.SUPABASE_KEY
        ) {
            install(Postgrest)
            install(Auth)
        }
    }

    // === Repositorios ===

    @Provides
    @Singleton
    fun provideAuthRepository(client: SupabaseClient): AuthRepository {
        return AuthRepositoryImpl(client)
    }

    @Provides
    @Singleton
    fun provideSettingsRepository(@ApplicationContext context: Context): SettingsRepository {
        return SettingsRepository(context)
    }

    @Provides
    @Singleton
    fun provideVehiclesRepository(client: SupabaseClient): VehiclesRepository {
        return VehiclesRepositoryImpl(client)
    }


}