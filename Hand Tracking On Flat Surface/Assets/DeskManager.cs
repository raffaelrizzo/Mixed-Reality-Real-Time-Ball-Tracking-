using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class Desk
{
    public float length;
    public float width;
    public Vector3 pivotPosition;
    public float yaw;
}

public class DeskManager : MonoBehaviour
{
    public GameObject visual;
    public Transform pivot;
    public float defaultWidth = 0.3f;
    public float defaultHeight = 0.01f;
    public float heightOffset = 0.03f;

    private CreationState creationState = CreationState.none;
    public enum CreationState {none, length, height, finish }

    private Vector3 startLengthPosition;
    public Transform creationHand;
    public OVRPassthroughLayer deskPassthrough;
    public OVRPassthroughLayer suroundPassthrough;

    public Material creationMat;
    public Material finishedMat;

    public List<GameObject> sceneObjectToAppear;

    private Camera cam;

    // Start is called before the first frame update
    void Start()
    {
        SetupPassthroughScene();
    }

    public void SetVisualMat(Material newMat)
    {
        visual.GetComponent<Renderer>().material = newMat;
    }

    // Update is called once per frame
    void Update()
    {
        switch (creationState)
        {
            case CreationState.none:
                visual.SetActive(false);


                if(OVRInput.GetDown(OVRInput.Button.SecondaryIndexTrigger))
                {
                    startLengthPosition = creationHand.position;
                    creationState = CreationState.length;
                }
                break;

            case CreationState.length:
                visual.SetActive(true);
                SetVisualMat(creationMat);

                //Scaling
                float distance = Vector3.ProjectOnPlane(creationHand.position - startLengthPosition, Vector3.up).magnitude;
                visual.transform.localScale = new Vector3(distance, defaultHeight, defaultWidth);

                //Position
                pivot.position = startLengthPosition + pivot.rotation * new Vector3(visual.transform.localScale.x / 2, 0, visual.transform.localScale.z / 2);

                //Rotation
                pivot.right = Vector3.ProjectOnPlane(creationHand.position - startLengthPosition,Vector3.up);

                if (!OVRInput.Get(OVRInput.Button.SecondaryIndexTrigger))
                {
                    creationState = CreationState.height;
                }

                break;
            case CreationState.height:

                //Le plan position Y suit le controlleur à un offset prêt.

                float maxY = Mathf.Min(pivot.position.y, creationHand.transform.position.y + heightOffset);

                pivot.position = new Vector3(pivot.position.x, maxY, pivot.position.z);

                if (OVRInput.GetDown(OVRInput.Button.SecondaryIndexTrigger))
                {
                    creationState = CreationState.finish;
                    SetupDeskScene();
                }

                break;
            case CreationState.finish:

                if (OVRInput.GetDown(OVRInput.Button.SecondaryIndexTrigger))
                {
                    deskPassthrough.RemoveSurfaceGeometry(visual);

                    startLengthPosition = creationHand.position;
                    creationState = CreationState.length;
                }

                break;

            default:
                break;
        }


        if(OVRInput.GetDown(OVRInput.Button.SecondaryIndexTrigger))
        {

        }
    }

    public void SetupPassthroughScene()
    {
        suroundPassthrough.hidden = false;
        deskPassthrough.hidden = true;
        //deskPassthrough.RemoveSurfaceGeometry(visual);
        SetVisualMat(creationMat);

        foreach (var item in sceneObjectToAppear)
        {
            item.SetActive(false);
        }

        Camera.main.clearFlags = CameraClearFlags.Color;
        Camera.main.backgroundColor = new Color(0, 0, 0, 0);
    }

    public void SetupDeskScene()
    {
        suroundPassthrough.hidden = true;
        deskPassthrough.hidden = false;
        deskPassthrough.AddSurfaceGeometry(visual,true);
        SetVisualMat(finishedMat);

        foreach (var item in sceneObjectToAppear)
        {
            item.SetActive(true);
        }

        Camera.main.clearFlags = CameraClearFlags.Skybox;
    }
}
