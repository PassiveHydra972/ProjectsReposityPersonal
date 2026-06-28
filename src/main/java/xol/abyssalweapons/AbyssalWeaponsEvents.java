package xol.abyssalweapons;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.component.CustomData;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import xol.abyssalweapons.damage.ModDamageTypes;
import xol.abyssalweapons.init.ItemInit;
import xol.abyssalweapons.item.RapierOfRevengeItem;
import xol.abyssalweapons.item.RazorOfInfinityItem;
import xol.abyssalweapons.item.SwordOfReverberanceItem;
import xol.abyssalweapons.item.TrueDamageSword;

@EventBusSubscriber(modid = AbyssalWeapons.MOD_ID, bus = EventBusSubscriber.Bus.GAME)
public class AbyssalWeaponsEvents {

    // ── True Damage routing ──────────────────────────────────────────────────

    @SubscribeEvent
    public static void onLivingAttack(LivingIncomingDamageEvent event) {
        // Skip if this is already our bypass-armour hit (prevents infinite recursion)
        if (event.getSource().typeHolder().is(ModDamageTypes.TRUE_BLADE)) return;

        Entity causingEntity = event.getSource().getEntity();
        if (!(causingEntity instanceof LivingEntity attacker)) return;

        ItemStack held = attacker.getMainHandItem();
        if (!(held.getItem() instanceof TrueDamageSword trueSword)) return;

        // Cancel the normal (armour-reduced) attack
        event.setCanceled(true);

        // Use the event amount: already includes Strength, Sharpness, critical hits, and
        // attack-charge scaling — we only strip the armour reduction.
        float damage = event.getAmount();

        LivingEntity target = event.getEntity();
        // Deliver true (bypass-armour) damage
        target.hurt(ModDamageTypes.trueBlade(target.level(), attacker, attacker), damage);

        // Fire post-hit hook for on-hit effects (e.g. Wither)
        trueSword.postTrueDamageHit(held, target, attacker);
    }

    // ── Astral Bastion damage reflection ─────────────────────────────────────

    /** Thorns damage type key — used to prevent reflection loops. */
    private static final ResourceKey<DamageType> THORNS_KEY = ResourceKey.create(
            Registries.DAMAGE_TYPE, ResourceLocation.withDefaultNamespace("thorns"));

    @SubscribeEvent
    public static void onAstralBastionReflect(LivingIncomingDamageEvent event) {
        // Skip if this is reflected (thorns) damage — prevents infinite loops
        if (event.getSource().typeHolder().is(THORNS_KEY)) return;

        LivingEntity target = event.getEntity();
        if (!(target instanceof Player player)) return;

        // Player must be holding the Astral Bastion in either hand
        boolean hasBastion = player.getMainHandItem().getItem() == ItemInit.ASTRAL_BASTION.get()
                          || player.getOffhandItem().getItem()  == ItemInit.ASTRAL_BASTION.get();
        if (!hasBastion) return;

        Entity attacker = event.getSource().getEntity();
        if (attacker == null) return; // Can't reflect environmental damage

        float damage = event.getAmount();
        event.setCanceled(true); // Player takes 0 damage
        // Reflect full damage back to the attacker
        attacker.hurt(target.level().damageSources().thorns(player), damage);
    }

    // ── Razor of Infinity: god-mode damage cancel ─────────────────────

    @SubscribeEvent
    public static void onRazorGodMode(LivingIncomingDamageEvent event) {
        if (!(event.getEntity() instanceof Player player)) return;
        // Skip our own true-blade hits to avoid confusing the routing
        if (event.getSource().typeHolder().is(ModDamageTypes.TRUE_BLADE)) return;

        ItemStack main = player.getMainHandItem();
        if (!(main.getItem() instanceof RazorOfInfinityItem)) return;

        CustomData data = main.get(DataComponents.CUSTOM_DATA);
        if (data == null) return;
        CompoundTag tag = data.copyTag();
        if (!tag.getBoolean(RazorOfInfinityItem.TAG_ACTIVE)) return;

        long now = player.level().getGameTime();
        if (now > tag.getLong(RazorOfInfinityItem.TAG_EXPIRY)) {
            // Expired: clear the flag
            tag.putBoolean(RazorOfInfinityItem.TAG_ACTIVE, false);
            main.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
            return;
        }

        // Still active: block all damage
        event.setCanceled(true);
    }

    // ── Sword of Reverberance passive effects ────────────────────────────────

    @SubscribeEvent
    public static void onPlayerTick(PlayerTickEvent.Post event) {
        Player player = event.getEntity();
        if (player.level().isClientSide) return;

        // Sword of Reverberance: passive buffs while held
        if (player.getMainHandItem().getItem() instanceof SwordOfReverberanceItem) {
            if (player.tickCount % 20 == 0) {
                int d = 40; // 2 s — refreshed each second while held
                player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,    d, 2, true, false, true));
                player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,      d, 2, true, false, true));
                player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, d, 2, true, false, true));
                player.addEffect(new MobEffectInstance(MobEffects.REGENERATION,      d, 0, true, false, true));
            }
        }

        // Rapier of Revenge: passive Strength II while held at ≤40% HP
        if (player.getMainHandItem().getItem() instanceof RapierOfRevengeItem) {
            if (player.getHealth() / player.getMaxHealth() <= 0.40f) {
                if (player.tickCount % 20 == 0) {
                    int d = 40; // 2 s refreshed
                    player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, d, 1, true, false, true)); // Strength II
                }
            }
        }
    }

    // ── Mirror Shield: partial reflect (75% to attacker, 25% to player) ──────

    @SubscribeEvent
    public static void onMirrorShieldReflect(LivingIncomingDamageEvent event) {
        if (event.getSource().typeHolder().is(THORNS_KEY)) return; // prevent reflect loops

        LivingEntity target = event.getEntity();
        if (!(target instanceof Player player)) return;
        if (!player.isBlocking()) return;

        boolean hasMirror = player.getMainHandItem().getItem() == ItemInit.MIRROR_SHIELD.get()
                         || player.getOffhandItem().getItem()  == ItemInit.MIRROR_SHIELD.get();
        if (!hasMirror) return;

        Entity attacker = event.getSource().getEntity();
        if (attacker == null) return;

        float damage = event.getAmount();
        event.setCanceled(true);
        // Attacker takes 75%, player takes 25% (through thorns to avoid armour recursion)
        attacker.hurt(target.level().damageSources().thorns(player), damage * 0.75f);
        player.hurt(target.level().damageSources().generic(), damage * 0.25f);
    }

    // ── Serpentine Shield: poison attacker on block ───────────────────────────

    @SubscribeEvent
    public static void onSerpentineShieldBlock(LivingIncomingDamageEvent event) {
        LivingEntity target = event.getEntity();
        if (!(target instanceof Player player)) return;
        if (!player.isBlocking()) return;

        boolean hasSerpentine = player.getMainHandItem().getItem() == ItemInit.SERPENTINE_SHIELD.get()
                             || player.getOffhandItem().getItem()  == ItemInit.SERPENTINE_SHIELD.get();
        if (!hasSerpentine) return;

        Entity attacker = event.getSource().getEntity();
        if (!(attacker instanceof LivingEntity livingAttacker)) return;

        // Poison the attacker
        livingAttacker.addEffect(new MobEffectInstance(MobEffects.POISON, 200, 2)); // Poison III, 10 s
    }
}