package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.UserProfile

interface AuthRepository {
    suspend fun signIn(email: String, password: String): Result<UserProfile>
    suspend fun getCurrentUserProfile(): Result<UserProfile>
    suspend fun signOut(): Result<Unit>
    fun isUserLoggedIn(): Boolean
}