package com.capstone.sigve.domain.repository

interface AuthRepository {
    suspend fun signIn(email: String, password: String): Result<Unit>
}