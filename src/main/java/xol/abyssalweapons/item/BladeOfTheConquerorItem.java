package xol.abyssalweapons.item;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;

/**
 * Blade of the Conqueror — 32 true dmg.
 * On kill: gain a Conquest stack (max 5), each adding +5 bonus magic damage on next hit.
 * Right-click: consume all stacks for Strength VI + Speed III (3 s per stack, 30 s cooldown).
 */
public class BladeOfTheConquerorItem extends TrueDamageSword {

    private static final int MAX_STACKS    = 5;
    private static final String TAG_STACKS = "ConquestStacks";

    public BladeOfTheConquerorItem() {
        super(Tiers.NETHERITE, 32.0f, 1.3f, new Item.Properties().stacksTo(1));
    }

    // ── Data Component helpers ────────────────────────────────────────────────

    private static int getStacks(ItemStack stack) {
        CustomData data = stack.get(DataComponents.CUSTOM_DATA);
        return (data != null) ? data.copyTag().getInt(TAG_STACKS) : 0;
    }

    private static void setStacks(ItemStack stack, int value) {
        CompoundTag tag = stack.has(DataComponents.CUSTOM_DATA)
                ? stack.get(DataComponents.CUSTOM_DATA).copyTag()
                : new CompoundTag();
        tag.putInt(TAG_STACKS, value);
        stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    }

    // ── True-damage post-hit: award stack on kill ─────────────────────────────

    @Override
    public void postTrueDamageHit(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        if (target.isDeadOrDying() && attacker instanceof Player player) {
            int current = getStacks(stack);
            if (current < MAX_STACKS) {
                setStacks(stack, current + 1);
                player.displayClientMessage(Component.literal(
                        "\u00a76\u00bb Conquest! Stacks: " + (current + 1) + "/" + MAX_STACKS + " \u00ab"), true);
            }
        }
    }

    // ── Each hit: deal bonus magic damage per stack ───────────────────────────

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        int stacks = getStacks(stack);
        boolean result = super.hurtEnemy(stack, target, attacker);
        if (result && stacks > 0 && !target.level().isClientSide) {
            target.hurt(target.level().damageSources().magic(), stacks * 5.0f);
        }
        return result;
    }

    // ── Right-click: consume stacks for a power burst ─────────────────────────

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        ItemStack stack = player.getItemInHand(hand);
        int stacks = getStacks(stack);
        if (stacks <= 0) {
            player.displayClientMessage(Component.literal("\u00a78No conquest stacks."), true);
            return InteractionResultHolder.pass(stack);
        }
        if (!level.isClientSide) {
            int duration = stacks * 60; // 3 s per stack
            player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,   duration, 5)); // Strength VI
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, duration, 2)); // Speed III
            setStacks(stack, 0);
            player.getCooldowns().addCooldown(this, 600); // 30 s
            player.displayClientMessage(Component.literal(
                    "\u00a76\u00bb Conquest unleashed! " + stacks + " stacks consumed! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    // ── Show stack count in item name ─────────────────────────────────────────

    @Override
    public Component getName(ItemStack stack) {
        int stacks = getStacks(stack);
        if (stacks > 0) {
            return Component.literal("\u00a76Blade of the Conqueror [" + stacks + "]");
        }
        return super.getName(stack);
    }
}
