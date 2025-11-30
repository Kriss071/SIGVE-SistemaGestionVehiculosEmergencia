package com.capstone.sigve.data.repository

import com.capstone.sigve.data.dto.UserProfileDto
import com.capstone.sigve.data.mapper.toDomain
import com.capstone.sigve.domain.model.UserProfile
import com.capstone.sigve.domain.repository.AuthRepository
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.auth.auth
import io.github.jan.supabase.auth.providers.builtin.Email
import io.github.jan.supabase.postgrest.postgrest
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val client: SupabaseClient
) : AuthRepository {

    override suspend fun signIn(email: String, password: String): Result<UserProfile> {
        return try {
            // Autenticar con Supabase Auth
            client.auth.signInWith(Email) {
                this.email = email
                this.password = password
            }
            
            // Obtener el perfil del usuario autenticado
            getCurrentUserProfile()
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getCurrentUserProfile(): Result<UserProfile> {
        return try {
            val userId = client.auth.currentUserOrNull()?.id
                ?: return Result.failure(Exception("Usuario no autenticado"))

            // Select con join a la tabla role usando foreign key
            val userProfileDto = client.postgrest["user_profile"]
                .select(columns = io.github.jan.supabase.postgrest.query.Columns.raw("*, role(*)")) {
                    filter {
                        eq("id", userId)
                    }
                }
                .decodeSingle<UserProfileDto>()

            Result.success(userProfileDto.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun signOut(): Result<Unit> {
        return try {
            client.auth.signOut()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun isUserLoggedIn(): Boolean {
        return client.auth.currentUserOrNull() != null
    }
}