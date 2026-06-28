package xol.abyssalweapons.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

public class WardenBlastProjectile extends Projectile {

    // Fraction of target's maximum health dealt per blast (default = 25 %)
    // Weapons can override this before adding the entity to the world.
    public float damageMultiplier = 0.25f;

    public WardenBlastProjectile(EntityType<? extends WardenBlastProjectile> type, Level level) {
        super(type, level);
    }

    public WardenBlastProjectile(EntityType<? extends WardenBlastProjectile> type, Level level, LivingEntity owner) {
        this(type, level);
        setOwner(owner);
        setPos(owner.getX(), owner.getEyeY() - 0.1, owner.getZ());
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder builder) {}

    @Override
    public void tick() {
        super.tick();

        // Particle trail (client only)
        if (level().isClientSide) {
            level().addParticle(ParticleTypes.SCULK_CHARGE_POP, getX(), getY(), getZ(), 0, 0, 0);
            level().addParticle(ParticleTypes.SONIC_BOOM,        getX(), getY(), getZ(), 0, 0, 0);
        }

        // Move the projectile
        Vec3 delta = getDeltaMovement();
        double nx = getX() + delta.x;
        double ny = getY() + delta.y;
        double nz = getZ() + delta.z;

        // Ray-cast for hits
        HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
        if (hit.getType() != HitResult.Type.MISS) {
            onHit(hit);
        }

        setPos(nx, ny, nz);

        // Lifetime: ~4 seconds or 80 blocks
        if (tickCount > 80) discard();
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        if (!level().isClientSide) {
            Entity target = result.getEntity();
            Entity owner  = getOwner();
            float damage = target instanceof LivingEntity le
                    ? le.getMaxHealth() * damageMultiplier
                    : 20.0f; // fallback for non-living targets
            // sonicBoom damage type bypasses armour in vanilla
            target.hurt(level().damageSources().sonicBoom(owner != null ? owner : this), damage);
            discard();
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        if (!level().isClientSide) discard();
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {}

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {}
}