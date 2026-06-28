package xol.abyssalweapons;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import xol.abyssalweapons.client.renderer.WardenBlastRenderer;
import xol.abyssalweapons.client.screen.NicroniumInfuserScreen;
import xol.abyssalweapons.init.EntityInit;
import xol.abyssalweapons.init.MenuInit;

@EventBusSubscriber(modid = AbyssalWeapons.MOD_ID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientSetup {

    @SubscribeEvent
    public static void register(RegisterMenuScreensEvent event) {
        event.register(MenuInit.NICRONIUM_INFUSER_MENU.get(), NicroniumInfuserScreen::new);
    }

    @SubscribeEvent
    public static void registerEntityRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(EntityInit.WARDEN_BLAST.get(), WardenBlastRenderer::new);
    }
}
