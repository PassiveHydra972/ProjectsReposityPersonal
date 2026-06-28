package xol.abyssalweapons.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.entity.WardenBlastProjectile;

/**
 * The WardenBlastProjectile is rendered through sculk/sonic-boom particles spawned
 * in the entity tick. This renderer is a no-op so the entity itself stays invisible.
 */
public class WardenBlastRenderer extends EntityRenderer<WardenBlastProjectile> {

    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(AbyssalWeapons.MOD_ID, "textures/misc/empty.png");

    public WardenBlastRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
    }

    @Override
    public void render(WardenBlastProjectile entity, float yaw, float partialTick,
                       PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        // Intentionally empty — particles handle the visual
    }

    @Override
    public ResourceLocation getTextureLocation(WardenBlastProjectile entity) {
        return TEXTURE;
    }
}