import { setRecoil } from "recoil-nexus";
import { GesturesService, PreMadeModelsService} from "../../clients/model"
import { gesturesAtom, preMadeModelsAtom } from "../atoms/apiAtoms";
import { OpenAPI as  OpenAPIModel} from "../../clients/model";
import { ModelsService } from "../../clients/model/services/ModelsService";
import { lastRefreshTimeAtom } from "../atoms/UIAtoms";
// import { lastRefreshTimeAtom } from "../atoms/UIAtoms";



export default {

    getPreMadeModels : async () => {
        const preMadeModels = await PreMadeModelsService.getPreMadeModelsPreMadeModelsGet();
        setRecoil(lastRefreshTimeAtom, new Date().getTime());
        setRecoil(preMadeModelsAtom, preMadeModels);
    },

    trainModel : async (model_id: string) => {
        console.log('sent')
        await ModelsService.postModelModelModelIdPost(model_id)
    },

    getGestures: async function () {
        try {
            // TODO get the list of gestures and their information
            const response = await GesturesService.getGesturesGesturesGet();
            // Set the gestures in the recoil atom
            setRecoil(gesturesAtom, response);
        } catch {
            console.log('Error getting gestures');
        }
    },

}
